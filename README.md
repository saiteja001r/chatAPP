# Chat App

This is a simple chat application built using **FastAPI** for the backend and **Streamlit** for the frontend. The application integrates a **Retrieval-Augmented Generation (RAG)** pipeline for enhanced conversational capabilities. It also includes utility functions such as speech-to-text conversion for a more interactive user experience.



## Features

- **Backend**: Built with FastAPI, providing a robust and scalable API for handling chat requests.
- **Frontend**: Developed using Streamlit, offering an intuitive and responsive user interface.
- **RAG Pipeline**: Integrates a Retrieval-Augmented Generation model for more context-aware and accurate responses also reranking.
- **Speech-to-Text**: Includes utility functions for converting speech to text, enhancing user interaction.
- **Database**: Utilizes a database for storing and retrieving chat history and other relevant data.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/chat_app.git
   cd chat_app
   
2. **set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   
5. **Run the backend server**:
   ```bash
   cd backend
   uvicorn app:app --reload
   
