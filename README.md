# PM Mockup Generator 🎨

An AI-powered mockup generation dashboard for Product Managers, powered by NVIDIA Nemotron. This application allows PMs to generate HTML mockups from natural language prompts, visualize them, collect stakeholder feedback, and iterate before passing to developers.

## 🏆 HackUTD Challenge Integration

### PNC Challenge: AI-Powered Productivity for Product Managers
This solution supports Product Managers in the **Prototyping & Testing** phase by:
- Generating wireframes and mockups instantly from natural language descriptions
- Enabling rapid iteration with AI-assisted refinement
- Facilitating stakeholder feedback collection
- Accelerating speed to market by reducing manual design work

### NVIDIA Challenge: Intelligent Agents with Multi-Step Workflows
This project demonstrates:
- **Reasoning beyond single-prompt conversation**: The AI understands context and generates complete, production-ready HTML mockups
- **Workflow orchestration**: Multi-step process from prompt → generation → feedback → refinement
- **Tool integration**: Integration with NVIDIA Nemotron API through Brev for rate limit management
- **Practical value**: Real-world application solving PM productivity challenges

## ✨ Features

- 🤖 **AI-Powered Generation**: Leverages NVIDIA Nemotron for intelligent mockup creation
- ⚡ **Instant Preview**: Real-time HTML rendering with iframe preview
- 💬 **Feedback System**: Collect and manage stakeholder comments
- 🔄 **AI Refinement**: Automatically refine mockups based on collected feedback
- 📥 **Export Ready**: Download HTML files to share with development teams
- 🎨 **Modern UI**: Beautiful, responsive dashboard built with React
- 🔧 **Rate Limit Management**: Uses Brev integration to handle API rate limits

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  - Dashboard: Prompt input & mockup generation              │
│  - MockupViewer: Preview, code view, feedback               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ REST API
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Backend (Flask)                            │
│  - API endpoints for generation & feedback                   │
│  - HTML to image conversion                                  │
│  - Feedback storage & management                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ API Calls
                     │
┌────────────────────▼────────────────────────────────────────┐
│              NVIDIA Nemotron (via Brev)                      │
│  - Natural language to HTML conversion                       │
│  - Mockup refinement based on feedback                       │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ 
- Node.js 16+
- npm or yarn
- NVIDIA API Key (get from [NVIDIA API Catalog](https://build.nvidia.com/))
- Brev account (optional, for enhanced rate limit management)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the `backend` directory:
   ```env
   NVIDIA_API_KEY=your_nvidia_api_key_here
   NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

5. **Run the backend**:
   ```bash
   python app.py
   ```
   
   Backend will be running on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory** (in a new terminal):
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```
   
   Frontend will be running on `http://localhost:3000`

## 📖 Usage Guide

### 1. Generate a Mockup

1. Open the dashboard at `http://localhost:3000`
2. Enter a project name (optional)
3. Describe your desired mockup in the prompt field. Be specific about:
   - Layout requirements
   - Features to include
   - Visual style preferences
   - Target audience
4. Click "Generate Mockup"
5. Wait for AI to generate your mockup (15-30 seconds)

**Example Prompts**:
- "Create a modern landing page for a fintech SaaS product with a hero section, features grid, and pricing table"
- "Design a dashboard for a project management tool with sidebar navigation, task cards, and progress charts"
- "Build a product page for an e-commerce site with image gallery, product details, and add to cart button"

### 2. Review and Collect Feedback

1. View the generated mockup in the Preview tab
2. Switch to Code tab to see the HTML source
3. Share with stakeholders and collect feedback:
   - Enter stakeholder name (optional)
   - Add feedback comments
   - Click "Send Feedback"

### 3. Refine with AI

1. After collecting feedback, click "Refine with AI"
2. The AI will analyze all feedback and generate an improved version
3. Review the refined mockup
4. Repeat the feedback loop as needed

### 4. Export for Development

1. Once satisfied with the mockup, click "Download HTML"
2. Share the HTML file with your development team
3. Developers can use it as a reference for implementation

## 🛠️ API Endpoints

### Health Check
```
GET /api/health
```
Returns API health status.

### Generate Mockup
```
POST /api/generate-mockup
Content-Type: application/json

{
  "prompt": "Description of the mockup",
  "project_name": "Optional project name"
}
```

### Get Mockup HTML
```
GET /api/mockups/{mockup_id}/html
```

### Get Mockup Screenshot
```
GET /api/mockups/{mockup_id}/screenshot
```

### Add Feedback
```
POST /api/mockups/{mockup_id}/feedback
Content-Type: application/json

{
  "feedback": "Feedback text",
  "author": "Name (optional)"
}
```

### Get Feedback
```
GET /api/mockups/{mockup_id}/feedback
```

### Refine Mockup
```
POST /api/refine-mockup
Content-Type: application/json

{
  "original_html": "Original HTML content",
  "feedback": ["Feedback item 1", "Feedback item 2"]
}
```

## 🔧 Configuration

### NVIDIA Nemotron Configuration

The application uses NVIDIA's Nemotron-4-340B-Instruct model. To configure:

1. Sign up at [NVIDIA API Catalog](https://build.nvidia.com/)
2. Generate an API key
3. Add it to your `.env` file

### Brev Integration (Optional)

For enhanced rate limit management through Brev:

1. Sign up at [Brev](https://brev.dev/)
2. Deploy the backend on Brev
3. Update `NVIDIA_API_URL` to use Brev's proxy endpoint

### Customization

- **Model parameters**: Edit `temperature` and `max_tokens` in `app.py`
- **Screenshot size**: Modify `size` parameter in `hti.screenshot()` calls
- **UI theme**: Update CSS files in `frontend/src/components/`

## 📁 Project Structure

```
hackutd_25/
├── backend/
│   ├── app.py                 # Flask backend with API endpoints
│   ├── requirements.txt       # Python dependencies
│   ├── mockups/              # Generated mockups storage
│   └── feedback.json         # Feedback storage
├── frontend/
│   ├── public/
│   │   └── index.html        # HTML template
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.js       # Main dashboard component
│   │   │   ├── Dashboard.css
│   │   │   ├── MockupViewer.js    # Mockup viewer component
│   │   │   └── MockupViewer.css
│   │   ├── App.js            # Root component
│   │   ├── App.css
│   │   ├── index.js          # React entry point
│   │   └── index.css
│   └── package.json          # Node dependencies
└── README.md                 # This file
```

## 🎯 Use Cases

1. **Rapid Prototyping**: Quickly generate mockups for stakeholder meetings
2. **A/B Testing**: Generate multiple versions to test with users
3. **Client Presentations**: Create professional mockups for proposals
4. **Developer Handoff**: Provide clear visual references to development teams
5. **Sprint Planning**: Visualize features before sprint commitment
6. **Stakeholder Alignment**: Get feedback early in the design process

## 🚧 Troubleshooting

### Backend Issues

**Error: "NVIDIA API Key not found"**
- Ensure your `.env` file exists and contains `NVIDIA_API_KEY`
- Restart the Flask server after adding environment variables

**Error: "Failed to generate mockup"**
- Check your NVIDIA API key is valid
- Verify you have available API credits
- Check internet connectivity
- Review Flask console for detailed error messages

### Frontend Issues

**Cannot connect to backend**
- Ensure Flask backend is running on port 5000
- Check `proxy` setting in `package.json` points to `http://localhost:5000`

**Mockup preview not loading**
- Check browser console for errors
- Ensure iframe sandbox permissions are correct
- Try refreshing the page

## 🔐 Security Notes

- Never commit your `.env` file to version control
- Keep your NVIDIA API key confidential
- The HTML preview uses iframe sandboxing for security
- Feedback data is stored locally (use a database in production)

## 🌟 Future Enhancements

- [ ] Database integration for persistent storage
- [ ] User authentication and project management
- [ ] Version control for mockup iterations
- [ ] Collaborative editing features
- [ ] Export to Figma/Sketch
- [ ] Mobile app support
- [ ] Real-time collaboration
- [ ] Template library
- [ ] AI-powered A/B test suggestions

## 📄 License

This project was created for HackUTD 2025.

## 🙏 Acknowledgments

- **NVIDIA** for providing the Nemotron AI model
- **PNC** for sponsoring the Product Manager productivity challenge
- **HackUTD** for organizing the hackathon
- **Brev** for rate limit management infrastructure

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the API documentation
3. Check Flask and React console logs
4. Refer to NVIDIA API documentation

---

Built with ❤️ for HackUTD 2025

