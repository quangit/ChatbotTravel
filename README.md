# Trợ lý Du lịch AI (Travel AI Assistant)

Một ứng dụng web chatbot thông minh giúp người dùng tìm hiểu về các địa điểm du lịch và món ăn ngon tại Việt Nam. Ứng dụng sử dụng công nghệ AI tiên tiến với khả năng hiểu cả văn bản và hình ảnh.

## 🌟 Tính năng chính

### Cho người dùng (End-User):
- **Chat thông minh**: Hỏi đáp về địa điểm du lịch, món ăn đặc sản
- **Nhận dạng hình ảnh**: Upload ảnh món ăn hoặc địa điểm để nhận thông tin
- **Gợi ý nhà hàng**: Đề xuất các quán ăn ngon với địa chỉ cụ thể
- **Tích hợp bản đồ**: Liên kết trực tiếp đến Google Maps
- **Text-to-Speech**: Nghe lại phản hồi của chatbot

### Cho quản trị viên (Admin):
- **Quản lý tri thức**: Upload tài liệu để cập nhật cơ sở dữ liệu
- **Hỗ trợ đa định dạng**: .txt, .pdf, .docx
- **Xử lý tự động**: Tự động phân tích và lưu trữ thông tin

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Browser                           │
│  ┌─────────────────────────────────────────────────────────┤
│  │        Frontend (HTML, CSS, JS)                        │
│  └─────────────────────────────────────────────────────────┤
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/HTTPS Requests
┌─────────────────────▼───────────────────────────────────────┐
│            FLASK APPLICATION SERVER                        │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │ Frontend Serving│    │     Backend API Routes          │ │
│  │ (templates &    │    │   (/api/chat, /api/tts, ...)    │ │
│  │  static files)  │    │                                 │ │
│  └─────────────────┘    └─────────────┬───────────────────┘ │
│                                       │                     │
│                         ┌─────────────▼───────────────────┐ │
│                         │      LangGraph AI Agent        │ │
│                         └─────────────┬───────────────────┘ │
│              ┌─────────────────────────┼─────────────────────┐
│              ▼                         ▼                     ▼
│    ┌─────────────────┐      ┌─────────────────┐   ┌──────────────────┐
│    │  Azure OpenAI   │      │    ChromaDB     │   │ Hugging Face TTS │
│    │ (LLM, Vision)   │      │ (Vector Store)  │   │     (API)        │
│    └─────────────────┘      └─────────────────┘   └──────────────────┘
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Công nghệ sử dụng

- **Backend**: Python, Flask
- **AI/ML**: Azure OpenAI, LangGraph, LangChain
- **Vector Database**: ChromaDB
- **Text-to-Speech**: Hugging Face API
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Document Processing**: PyPDF2, python-docx

## 📋 Yêu cầu hệ thống

- Python 3.8+
- Azure OpenAI API access
- Hugging Face API token
- 2GB RAM (tối thiểu)
- 1GB dung lượng ổ cứng

## 🚀 Hướng dẫn cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd ChatbotTravel
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình môi trường
Tạo file `.env` và cập nhật các thông tin sau:
```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-01

# Hugging Face Configuration
HUGGINGFACE_API_TOKEN=your_huggingface_api_token

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
ADMIN_PASSWORD=admin123

# ChromaDB Configuration
CHROMADB_PATH=./data/chroma_db
```

### 4. Khởi chạy ứng dụng
```bash
python app.py
```

Truy cập: http://localhost:5000

## 📖 Hướng dẫn sử dụng

### Cho người dùng:
1. Truy cập trang chính
2. Nhập câu hỏi về du lịch hoặc upload ảnh
3. Nhận thông tin chi tiết và gợi ý
4. Click vào liên kết bản đồ để xem vị trí
5. Sử dụng nút loa để nghe phản hồi

### Cho quản trị viên:
1. Truy cập `/admin`
2. Đăng nhập bằng mật khẩu admin
3. Upload tài liệu (.txt, .pdf, .docx)
4. Hệ thống sẽ tự động xử lý và cập nhật cơ sở tri thức

## 🔧 Cấu trúc dự án

```
ChatbotTravel/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── routes.py            # API routes & web routes
│   ├── models.py            # ChromaDB & document processing
│   ├── ai_agent.py          # LangGraph AI agent
│   └── tts_service.py       # Text-to-speech service
├── templates/
│   ├── base.html            # Base template
│   ├── index.html           # Chat interface
│   ├── admin_login.html     # Admin login
│   └── admin.html           # Admin dashboard
├── static/
│   ├── css/
│   │   └── style.css        # Main stylesheet
│   └── js/
│       ├── chat.js          # Chat interface logic
│       └── admin.js         # Admin interface logic
├── uploads/                 # Temporary upload directory
├── data/                    # ChromaDB data directory
├── app.py                   # Main application entry point
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## 🔒 Bảo mật

- Tất cả API keys được lưu trữ trong biến môi trường
- Giao diện admin được bảo vệ bằng mật khẩu
- Validation đầu vào để tránh XSS
- Upload file được kiểm tra định dạng và kích thước

## 🚦 API Endpoints

- `GET /` - Giao diện chat chính
- `GET /admin` - Giao diện quản trị
- `POST /api/chat` - Xử lý tin nhắn chat
- `POST /api/tts` - Text-to-speech
- `POST /api/upload` - Upload tài liệu (Admin only)
- `POST /api/image_upload` - Upload hình ảnh

## 🐛 Troubleshooting

### Lỗi kết nối Azure OpenAI:
- Kiểm tra endpoint và API key
- Đảm bảo deployment name chính xác
- Kiểm tra quota và limits

### ChromaDB không khởi tạo được:
- Tạo thư mục `data/` nếu chưa có
- Kiểm tra quyền ghi file
- Xóa thư mục `data/chroma_db` và khởi động lại

### TTS không hoạt động:
- Kiểm tra Hugging Face API token
- Đảm bảo kết nối internet ổn định
- Thử với văn bản ngắn hơn

## 📈 Phát triển tương lai

- [ ] Hỗ trợ đa ngôn ngữ
- [ ] Tích hợp đăng nhập người dùng
- [ ] Lưu lịch sử trò chuyện
- [ ] API cho mobile app
- [ ] Tích hợp booking trực tuyến
- [ ] Hỗ trợ voice input

## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo issue hoặc pull request.

## 📞 Liên hệ

- Email: your-email@example.com
- Website: your-website.com

---
*Được phát triển với ❤️ cho cộng đồng du lịch Việt Nam*
