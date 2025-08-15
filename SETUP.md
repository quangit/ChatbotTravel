# 🚀 Hướng dẫn cài đặt nhanh

## 1. Cài đặt dependencies

```bash
pip install flask python-dotenv openai chromadb langchain langchain-openai langchain-community langgraph PyPDF2 python-docx requests Pillow werkzeug
```

## 2. Cấu hình environment

Sửa file `.env` với thông tin thực của bạn:

```env
# Azure OpenAI Configuration (BẮT BUỘC)
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o  # hoặc tên deployment của bạn
AZURE_OPENAI_API_VERSION=2024-02-01

# Hugging Face Configuration (TÙY CHỌN - cho TTS)
HUGGINGFACE_API_TOKEN=your_hf_token_here

# Flask Configuration
FLASK_SECRET_KEY=your_super_secret_key_here
ADMIN_PASSWORD=admin123  # Đổi mật khẩu này!

# ChromaDB Configuration
CHROMADB_PATH=./data/chroma_db
```

## 3. Khởi tạo database

```bash
python init_database.py
```

## 4. Chạy ứng dụng

```bash
python app.py
```

## 5. Truy cập ứng dụng

- **Chat Interface**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin (password: admin123)

## ⚠️ Lưu ý quan trọng

1. **Azure OpenAI**: Cần có API key và deployment hợp lệ
2. **Vision API**: Cần deployment gpt-4-vision hoặc tương tự cho nhận dạng ảnh
3. **Embedding**: Cần deployment text-embedding-3-small hoặc tương tự
4. **Hugging Face**: Không bắt buộc, chỉ cần cho tính năng TTS

## 🔧 Xử lý lỗi thường gặp

### Import Error:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### ChromaDB Error:
```bash
# Xóa folder data và tạo lại
rmdir /s data
mkdir data
python init_database.py
```

### Azure OpenAI Connection Error:
- Kiểm tra endpoint URL (phải có https://)
- Kiểm tra API key
- Kiểm tra tên deployment
- Đảm bảo có quyền truy cập resource

## 📚 Test nhanh

1. Khởi động app: `python app.py`
2. Mở browser: http://localhost:5000
3. Hỏi: "Hồ Gươm có gì hay?"
4. Upload ảnh món ăn bất kỳ
5. Vào admin panel và upload file .txt mẫu
