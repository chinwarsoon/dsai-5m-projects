"""
LLM Integration with Ollama for RAG Pipeline
Implements local LLM integration using Ollama and llama3.2:3b
"""

import requests
from typing import Dict, Any, List, Optional, Union
from .logger import Logger


class OllamaLLM:
    """
    Ollama LLM integration for local inference
    """
    
    def __init__(self, config: Dict[str, Any], logger: Logger):
        """
        Initialize Ollama LLM
        
        Args:
            config: Configuration from schema
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.logger.enter_function("OllamaLLM.__init__")
        
        self.llm_config = config.get('llm', {})
        self.base_url = self.llm_config.get('base_url', 'http://localhost:11434')
        self.model_name = self.llm_config.get('model', 'llama3.2:3b')
        self.temperature = self.llm_config.get('temperature', 0.7)
        self.max_tokens = self.llm_config.get('max_tokens', 2000)
        
        self.logger.info(
            f"Initializing Ollama LLM with model: {self.model_name}",
            "OllamaLLM.__init__"
        )
        self.logger.add_trace_entry(
            "llm_model",
            self.model_name,
            "llm_initialization",
            "success"
        )
        
        # Test Ollama connection
        self._test_connection()
        
        self.logger.exit_function("OllamaLLM.__init__")
    
    def _test_connection(self) -> None:
        """
        Test Ollama connection
        
        Raises:
            Exception: If connection fails
        """
        self.logger.trace("Testing Ollama connection", "OllamaLLM._test_connection")
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.logger.info("Ollama connection successful", "OllamaLLM._test_connection")
            else:
                self.logger.warning(
                    f"Ollama returned status {response.status_code}",
                    "OllamaLLM._test_connection"
                )
        except Exception as e:
            self.logger.warning(
                f"Ollama connection test failed: {str(e)}",
                "OllamaLLM._test_connection"
            )
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text using Ollama
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (overrides default)
            max_tokens: Maximum tokens to generate (overrides default)
            
        Returns:
            Generated text
        """
        self.logger.enter_function("OllamaLLM.generate")
        self.logger.trace(f"Generating with prompt length: {len(prompt)}", "OllamaLLM.generate")
        
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temp,
                        "num_predict": max_tok
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')
                
                self.logger.add_trace_entry(
                    "generated_text_length",
                    len(generated_text),
                    "llm_generation",
                    "success"
                )
                
                self.logger.exit_function("OllamaLLM.generate")
                return generated_text
            else:
                self.logger.error(
                    f"Ollama generation failed with status {response.status_code}",
                    "OllamaLLM.generate"
                )
                self.logger.exit_function("OllamaLLM.generate")
                return ""
                
        except Exception as e:
            self.logger.error(f"Ollama generation error: {str(e)}", "OllamaLLM.generate")
            self.logger.exit_function("OllamaLLM.generate")
            return ""
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Chat with Ollama using message format
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (overrides default)
            max_tokens: Maximum tokens to generate (overrides default)
            
        Returns:
            Generated response
        """
        self.logger.enter_function("OllamaLLM.chat")
        self.logger.info(f"Chat with {len(messages)} messages", "OllamaLLM.chat")
        
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temp,
                        "num_predict": max_tok
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('message', {}).get('content', '')
                
                self.logger.add_trace_entry(
                    "chat_response_length",
                    len(generated_text),
                    "llm_chat",
                    "success"
                )
                
                self.logger.exit_function("OllamaLLM.chat")
                return generated_text
            else:
                self.logger.error(
                    f"Ollama chat failed with status {response.status_code}",
                    "OllamaLLM.chat"
                )
                self.logger.exit_function("OllamaLLM.chat")
                return ""
                
        except Exception as e:
            self.logger.error(f"Ollama chat error: {str(e)}", "OllamaLLM.chat")
            self.logger.exit_function("OllamaLLM.chat")
            return ""


class RAGPipeline:
    """
    RAG Pipeline combining retrieval and generation
    """
    
    def __init__(
        self,
        retriever,
        llm: OllamaLLM,
        config: Dict[str, Any],
        logger: Logger
    ):
        """
        Initialize RAG pipeline
        
        Args:
            retriever: Retriever instance for document retrieval
            llm: Ollama LLM instance
            config: Configuration from schema
            logger: Logger instance
        """
        self.retriever = retriever
        self.llm = llm
        self.config = config
        self.logger = logger
        self.logger.enter_function("RAGPipeline.__init__")
        
        self.rag_config = config.get('rag', {})
        self.top_k = self.rag_config.get('top_k', 5)
        self.score_threshold = self.rag_config.get('score_threshold', 0.0)
        
        self.logger.info("RAG pipeline initialized", "RAGPipeline.__init__")
        self.logger.exit_function("RAGPipeline.__init__")
    
    def assemble_context(
        self,
        retrieved_docs: List[Dict[str, Any]],
        max_context_length: int = 2000
    ) -> str:
        """
        Assemble context from retrieved documents
        
        Args:
            retrieved_docs: List of retrieved documents with metadata
            max_context_length: Maximum context length in characters
            
        Returns:
            Assembled context string
        """
        self.logger.enter_function("RAGPipeline.assemble_context")
        self.logger.info(
            f"Assembling context from {len(retrieved_docs)} documents",
            "RAGPipeline.assemble_context"
        )
        
        context_parts = []
        current_length = 0
        
        for doc in retrieved_docs:
            doc_text = doc.get('document', '')
            metadata = doc.get('metadata', {})
            
            # Format document with metadata
            if metadata:
                metadata_str = " | ".join([f"{k}: {v}" for k, v in metadata.items()])
                formatted_doc = f"[{metadata_str}] {doc_text}"
            else:
                formatted_doc = doc_text
            
            # Check if adding this document would exceed max length
            if current_length + len(formatted_doc) > max_context_length:
                break
            
            context_parts.append(formatted_doc)
            current_length += len(formatted_doc)
        
        context = "\n\n".join(context_parts)
        
        self.logger.add_trace_entry(
            "context_length",
            len(context),
            "context_assembly",
            "success"
        )
        
        self.logger.exit_function("RAGPipeline.assemble_context")
        return context
    
    def create_prompt(
        self,
        query: str,
        context: str,
        prompt_template: Optional[str] = None
    ) -> str:
        """
        Create prompt for LLM
        
        Args:
            query: User query
            context: Retrieved context
            prompt_template: Custom prompt template
            
        Returns:
            Formatted prompt
        """
        self.logger.enter_function("RAGPipeline.create_prompt")
        
        if prompt_template is None:
            prompt_template = """You are a helpful assistant for querying document submittal register data. Use the following context to answer the user's question.

Context:
{context}

Question: {query}

Answer:"""
        
        prompt = prompt_template.format(context=context, query=query)
        
        self.logger.exit_function("RAGPipeline.create_prompt")
        return prompt
    
    def query(
        self,
        user_query: str,
        k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        where: Optional[Dict[str, Any]] = None,
        prompt_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute RAG query
        
        Args:
            user_query: User's question
            k: Number of documents to retrieve
            score_threshold: Minimum similarity score
            where: Metadata filter conditions
            prompt_template: Custom prompt template
            
        Returns:
            Dictionary with answer, context, and sources
        """
        self.logger.enter_function("RAGPipeline.query")
        self.logger.info(f"RAG query: {user_query[:50]}...", "RAGPipeline.query")
        
        # Set default parameters
        k = k if k is not None else self.top_k
        score_threshold = score_threshold if score_threshold is not None else self.score_threshold
        
        # Retrieve relevant documents
        retrieved_results = self.retriever.query(
            query_text=user_query,
            k=k,
            score_threshold=score_threshold,
            where=where
        )
        
        # Format results
        formatted_results = self.retriever.format_results(retrieved_results)
        
        # Assemble context
        context = self.assemble_context(formatted_results)
        
        # Create prompt
        prompt = self.create_prompt(user_query, context, prompt_template)
        
        # Generate answer
        answer = self.llm.generate(prompt)
        
        result = {
            'answer': answer,
            'context': context,
            'sources': formatted_results,
            'query': user_query
        }
        
        self.logger.add_trace_entry(
            "rag_query_completed",
            True,
            "rag_pipeline",
            "success"
        )
        
        self.logger.exit_function("RAGPipeline.query")
        return result
    
    def query_with_grouping(
        self,
        user_query: str,
        group_by: str,
        k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        prompt_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute RAG query with grouping
        
        Args:
            user_query: User's question
            group_by: Column to group results by
            k: Number of results per group
            score_threshold: Minimum similarity score
            prompt_template: Custom prompt template
            
        Returns:
            Dictionary with grouped answers
        """
        self.logger.enter_function("RAGPipeline.query_with_grouping")
        self.logger.info(
            f"RAG query with grouping by {group_by}",
            "RAGPipeline.query_with_grouping"
        )
        
        # Use advanced retriever for grouping
        if hasattr(self.retriever, 'query_with_grouping'):
            grouped_results = self.retriever.query_with_grouping(
                query_text=user_query,
                group_by=group_by,
                k=k if k else self.top_k,
                score_threshold=score_threshold if score_threshold else self.score_threshold
            )
        else:
            self.logger.warning(
                "Retriever does not support grouping, using standard query",
                "RAGPipeline.query_with_grouping"
            )
            standard_results = self.retriever.query(
                query_text=user_query,
                k=k if k else self.top_k * 10,
                score_threshold=score_threshold if score_threshold else self.score_threshold
            )
            grouped_results = {'default': standard_results}
        
        # Generate answer for each group
        grouped_answers = {}
        for group_name, group_data in grouped_results.items():
            formatted_results = self.retriever.format_results(group_data)
            context = self.assemble_context(formatted_results)
            prompt = self.create_prompt(user_query, context, prompt_template)
            answer = self.llm.generate(prompt)
            
            grouped_answers[group_name] = {
                'answer': answer,
                'context': context,
                'sources': formatted_results
            }
        
        result = {
            'grouped_answers': grouped_answers,
            'query': user_query,
            'group_by': group_by
        }
        
        self.logger.exit_function("RAGPipeline.query_with_grouping")
        return result


def get_ollama_llm(config: Dict[str, Any], logger: Logger) -> OllamaLLM:
    """
    Get Ollama LLM instance
    
    Args:
        config: Configuration from schema
        logger: Logger instance
        
    Returns:
        OllamaLLM instance
    """
    return OllamaLLM(config, logger)


def get_rag_pipeline(
    retriever,
    llm: OllamaLLM,
    config: Dict[str, Any],
    logger: Logger
) -> RAGPipeline:
    """
    Get RAG pipeline instance
    
    Args:
        retriever: Retriever instance
        llm: Ollama LLM instance
        config: Configuration from schema
        logger: Logger instance
        
    Returns:
        RAGPipeline instance
    """
    return RAGPipeline(retriever, llm, config, logger)
