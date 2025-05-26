# 💬 Streamlit Web Chatbot Deployment Guide
## Keep python version more than 3.8 best 3.13.2 while creating virtual env.
This repository contains a deployable Streamlit chatbot app powered by Cohere API and MongoDB. Follow the step-by-step guide below to test it locally, deploy it on Render, and embed it into any website.
 
## ✅ Step 1: Clone This Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

Replace the URL with your actual repository link if different.
 
## 📦 Step 2: Install Required Dependencies

Ensure you have Python and pip installed, then run:
 
```bash
pip install -r requirements.txt
```

## 🧪 Step 3: Run the App Locally

To test the chatbot on your local machine:
 
```bash
streamlit run frontend.py
```

## 🔐 Step 4: Create a .env File Locally

In the root of your project, create a `.env` file and add the following environment variables:
 
```env
COHERE_API_KEY="your_cohere_api_key"
MONGO_URI="mongodb+srv://chatbot_user:chatbot123@chatbotcluster.rw94opl.mongodb.net/?retryWrites=true&w=majority&appName=ChatbotCluster"
DB_NAME="SessionData"
```

Replace `your_cohere_api_key` with your actual Cohere API Key.
 
## 🚀 Step 5: Convert This Repo Into Your Own Public Repo

Create a new repository on your GitHub account and link this code:
 
```bash
git remote remove origin
git remote add origin https://github.com/your-username/your-repo-name.git
git push -u origin main
```

## 🌐 Step 6: Deploy to Render

1. Go to Render Web Services
 
2. Login or Signup with your GitHub account.
 
3. Connect your GitHub and select your chatbot repository.
 
4. Set the Start Command:
 
   ```bash
   streamlit run frontend.py
   ```

5. Set Instance Type: Free
 
6. Add Environment Variables:
   - `COHERE_API_KEY`
   - `MONGO_URI`
   - `DB_NAME`
 
7. Click on Deploy Web Service
 
8. Wait for deployment — you will get a live URL once it's complete.
 
## 🌍 Step 7: Embed Chatbot in Your Website

Use the following snippet to embed the chatbot widget into any webpage:
 
```html
<!-- Chatbot Dialog Box Embed Code -->
<style>
  #chatbot-button {
    position: fixed;
    bottom: 25px;
    right: 25px;
    background-color: #007bff;
    color: white;
    padding: 12px 18px;
    border: none;
    border-radius: 50px;
    cursor: pointer;
    font-size: 16px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    z-index: 9999;
  }
 
  #chatbot-container {
    display: none;
    position: fixed;
    bottom: 90px;
    right: 25px;
    width: 380px;
    height: 520px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 6px 15px rgba(0,0,0,0.3);
    overflow: hidden;
    z-index: 9999;
  }
 
  #chatbot-container iframe {
    width: 100%;
    height: 100%;
    border: none;
  }
 
  #chatbot-close {
    position: absolute;
    top: 8px;
    right: 12px;
    background: transparent;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: #444;
    z-index: 10000;
  }
</style>
 
<div id="chatbot-container">
<button id="chatbot-close">&times;</button>
<iframe src="ADD_YOUR_LINK_HERE" allow="microphone; autoplay"></iframe>
</div>
 
<button id="chatbot-button">Chat with us</button>
 
<script>
  const chatbotButton = document.getElementById('chatbot-button');
  const chatbotContainer = document.getElementById('chatbot-container');
  const chatbotClose = document.getElementById('chatbot-close');
 
  chatbotButton.onclick = () => {
    chatbotContainer.style.display = 'block';
  };
 
  chatbotClose.onclick = () => {
    chatbotContainer.style.display = 'none';  
  };
</script>
```

👉 Replace `ADD_YOUR_LINK_HERE` with your actual Render deployment URL
(e.g., `https://your-app-name.onrender.com`)
 
## ✅ You're Done!

🎉 Your Streamlit chatbot is now live and embeddable!
Feel free to share, customize, or enhance it as needed.
 