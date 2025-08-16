# Weather Integration Feature

## Tổng quan

Tính năng mới được thêm vào ChatbotTravel để cung cấp thông tin thời tiết real-time cho các địa điểm du lịch.

## Cách hoạt động

### 1. LangGraph Workflow mới:
```
analyze_input → retrieve_docs → generate_response → get_weather → final_response
```

### 2. Các node mới:
- **get_weather**: Node lấy thông tin thời tiết (sau generate_response)
- **final_response**: Node tạo response cuối cùng kết hợp thông tin thời tiết
- **_extract_location**: Method trích xuất địa điểm từ LLM response
- **_get_weather_info**: Method gọi OpenWeather API
- **_get_weather_advice**: Method tạo lời khuyên dựa trên thời tiết

## Cấu hình

### 1. Thêm OpenWeather API Key vào `.env`:
```env
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

### 2. Đăng ký OpenWeather API:
1. Truy cập [OpenWeatherMap](https://openweathermap.org/api)
2. Tạo tài khoản miễn phí
3. Lấy API key từ dashboard
4. Thêm vào file `.env`

## Tính năng

### 1. Trích xuất địa điểm thông minh:
- Sử dụng LLM để phân tích query và documents
- Trích xuất tên thành phố/địa điểm du lịch
- Chuyển đổi sang tiếng Anh cho API call

### 2. Thông tin thời tiết bao gồm:
- 🌡️ Nhiệt độ hiện tại và cảm giác
- 🌤️ Mô tả thời tiết (bằng tiếng Việt)
- 💧 Độ ẩm
- 💨 Tốc độ gió
- 📍 Vị trí chính xác

### 3. Tích hợp vào response:
- AI sẽ sử dụng thông tin thời tiết để đưa ra lời khuyên
- Tự động bao gồm trong câu trả lời khi liên quan
- Gợi ý trang phục, hoạt động phù hợp

## Ví dụ sử dụng

### Input:
```
"Tôi muốn đi du lịch Đà Nẵng, thời tiết thế nào?"
```

### Output:
```
🌤️ **Thời tiết tại Da Nang, VN:**
- Nhiệt độ: 28°C (cảm giác như 32°C)
- Thời tiết: trời quang mây
- Độ ẩm: 78%
- Tốc độ gió: 3.5 m/s

Đà Nẵng hiện tại có thời tiết khá đẹp với nhiệt độ 28°C, rất phù hợp cho du lịch...
[Thông tin chi tiết về Đà Nẵng và lời khuyên dựa trên thời tiết]
```

## Test

Chạy test script để kiểm tra tính năng:

```bash
python test_weather.py
```

## Flow xử lý

1. **User Input**: "Thời tiết ở Hà Nội thế nào?"

2. **analyze_input**: Xác định query type = "text"

3. **retrieve_docs**: Lấy documents về Hà Nội từ ChromaDB

4. **generate_response**: Tạo response ban đầu về Hà Nội (không có thời tiết)

5. **get_weather**: 
   - Extract "Hanoi" từ response đã được tạo
   - Call OpenWeather API
   - Format thông tin thời tiết

6. **final_response**: 
   - Kết hợp response ban đầu + thông tin thời tiết
   - Thêm lời khuyên dựa trên thời tiết

## Error Handling

- Graceful fallback nếu API key không có
- Timeout protection cho API calls  
- Error logging cho debugging
- Default behavior nếu không extract được location

## Lợi ích

- ✅ Thông tin thời tiết real-time
- ✅ Lời khuyên du lịch phù hợp với thời tiết
- ✅ Tích hợp seamless với existing workflow  
- ✅ Hỗ trợ multiple Vietnamese cities
- ✅ Robust error handling
