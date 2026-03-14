# 🏢 HR Policy Expert Assistant (HR-PEA)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.0-orange.svg)](https://langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.20-purple.svg)](https://langchain.ai/)

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Multi-Agent Workflow](#-multi-agent-workflow)
- [Database Schema](#-database-schema)
- [API Documentation](#-api-documentation)
- [Installation Guide](#-installation-guide)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🎯 Overview

**HR Policy Expert Assistant (HR-PEA)** is a sophisticated multi-agent AI system designed to help employees and HR professionals quickly find answers to complex HR policy questions. Unlike simple Q&A bots, HR-PEA uses a collaborative multi-agent workflow to decompose complex queries, retrieve relevant information from multiple sources, and generate comprehensive, traceable answers.

### Real-World Use Case
A multinational company with employees across different states needs to answer questions like:
- *"What's the remote work policy for California vs New York employees?"*
- *"Compare parental leave policies and state-specific benefits"*
- *"Find all policies mentioning overtime approval with recent exceptions"*

HR-PEA intelligently breaks down these questions, searches through HR documents, policies, and uploaded files, and provides accurate answers with reasoning traces.

---

## ✨ Features

### Core Capabilities
- ✅ **Multi-Agent Orchestration** - Planner, Retriever, Reranker, and Summarizer agents collaborate
- ✅ **Hybrid Search** - Combines vector similarity and keyword search for accurate retrieval
- ✅ **Multi-Format File Ingestion** - Upload PDF, DOCX, TXT, CSV, JSON files
- ✅ **Smart Caching** - 7-day query cache to reduce API costs
- ✅ **User Authentication** - JWT-based secure access
- ✅ **Query History** - Track all your questions and answers
- ✅ **Model Agnostic** - Switch between OpenAI, DeepSeek, or Gemini with one config change
- ✅ **Real-time Processing** - Background file indexing with status updates

### Technical Highlights
- 🔄 **LangGraph Workflow** - Stateful multi-agent orchestration
- 🧠 **LangChain Integration** - Seamless LLM and embedding management
- 📊 **pgvector** - High-performance vector similarity search
- 🐳 **Dockerized** - One-command deployment
- 📝 **LangSmith Ready** - Optional tracing for debugging

---

## 🏗 System Architecture

### High-Level Design (HLD)
