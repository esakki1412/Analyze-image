# Analyze-image

## Description

This project is a desktop application built with **Python**, **Tkinter**, and **Azure AI Vision** that allows users to analyze images for captions, tags, objects, and people. The app supports both local file uploads and image URLs.

## 🚀 Features
- **File Input**: Load an image from your computer.
- **URL Input**: Load an image from an online link.
- **Azure AI Vision Analysis**:
  - Main caption and dense captions
  - Tags with confidence levels
  - Object detection with bounding boxes
  - People detection with bounding boxes
- **Tabbed Image Views**:
  - Original Image
  - Object Detection annotations
  - People Detection annotations

## 📦 Requirements
- Python 3.8+
- Azure AI Vision Key & Endpoint
- The following Python packages:
  ```bash
  pip install pillow python-dotenv azure-ai-vision azure-core requests
  ```

## 🔑 Environment Variables
Create a `.env` file in the project root and add your Azure AI Vision credentials:

```env
AI_SERVICE_ENDPOINT=your_azure_endpoint_here
AI_SERVICE_KEY=your_azure_key_here
```

## ▶️ How to Run
1. Clone this repository:
   ```bash
   git clone https://github.com/esakki1412/Analyze-image
   cd Analyze-image
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python Analyze image.py
   ```

## 📂 Project Structure
```
.
├── Analyze image.py     # Main Tkinter application code
├── .env                 # Azure AI Vision credentials
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```




## 🛠️ Tech Stack
- **Python**
- **Tkinter**
- **Azure AI Vision**
- **Pillow** for image processing
- **Requests** for URL image loading

## 📜 License
This project is licensed under the Apache 2.0 License.
