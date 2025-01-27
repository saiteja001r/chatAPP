# Chat App

This is a simple chat application built using **FastAPI** for the backend and **Streamlit** for the frontend. The application integrates a **Retrieval-Augmented Generation (RAG)** pipeline for enhanced conversational capabilities. It also includes utility functions such as speech-to-text conversion for a more interactive user experience.

## Project Structure


chat_app/
│
├── backend/
│ ├── init.py
│ ├── app.py # FastAPI backend code
│ ├── database.py # Database setup and utilities
│ └── models.py # Pydantic models for API requests/responses
│
├── frontend/
│ ├── init.py
│ ├── app.py # Streamlit frontend code
│ ├── rag.py # RAG pipeline initialization
│ └── utils.py # Utility functions (e.g., speech-to-text)
│
├── runner.py # Runner script to start the Streamlit app
├── requirements.txt # List of dependencies
├── README.md # Project documentation
└── .gitignore # Files/folders to ignore in Git


## Features

- **Backend**: Built with FastAPI, providing a robust and scalable API for handling chat requests.
- **Frontend**: Developed using Streamlit, offering an intuitive and responsive user interface.
- **RAG Pipeline**: Integrates a Retrieval-Augmented Generation model for more context-aware and accurate responses.
- **Speech-to-Text**: Includes utility functions for converting speech to text, enhancing user interaction.
- **Database**: Utilizes a database for storing and retrieving chat history and other relevant data.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/chat_app.git
   cd chat_app
2. ** set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
