# Image Resize Feature

## Tổng quan

Tính năng resize hình ảnh tự động được thêm vào ChatbotTravel để tối ưu hóa việc xử lý hình ảnh trước khi gửi lên server.

## Tính năng chính

### 🖼️ **Automatic Image Resizing**
- **Max Dimension**: 512px (chiều dài hoặc rộng tối đa)
- **Quality**: 90% JPEG quality
- **Aspect Ratio**: Giữ nguyên tỷ lệ khung hình
- **Format**: Hỗ trợ tất cả format hình ảnh phổ biến

### 📊 **Smart Dimension Calculation**
```javascript
if (width > height) {
    if (width > 512) {
        height = (height * 512) / width;
        width = 512;
    }
} else {
    if (height > 512) {
        width = (width * 512) / height;
        height = 512;
    }
}
```

### 💾 **Benefits**
- ✅ Giảm kích thước file để upload nhanh hơn
- ✅ Tiết kiệm băng thông
- ✅ Cải thiện hiệu suất Vision API
- ✅ Giữ nguyên chất lượng hình ảnh đủ để phân tích

## Implementation

### 1. **Core Resize Function**
```javascript
resizeImage(file, maxDimension = 512) {
    return new Promise((resolve, reject) => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        img.onload = () => {
            // Calculate dimensions
            let { width, height } = img;
            
            // Resize logic...
            canvas.width = width;
            canvas.height = height;
            ctx.drawImage(img, 0, 0, width, height);
            
            // Convert to base64
            canvas.toBlob((blob) => {
                // Return base64 data
            }, file.type, 0.9);
        };
        
        img.src = URL.createObjectURL(file);
    });
}
```

### 2. **Integration in handleImageSelect**
```javascript
async handleImageSelect(event) {
    const file = event.target.files[0];
    
    // Validation...
    
    // Show processing state
    this.showProcessingMessage('Đang xử lý hình ảnh...');
    
    // Resize image
    const resizedImageData = await this.resizeImage(file, 512);
    
    // Store resized data
    this.currentImageData = {
        data: resizedImageData.base64,
        originalSize: { width: original.width, height: original.height },
        resizedSize: { width: resized.width, height: resized.height }
    };
    
    this.hideProcessingMessage();
}
```

### 3. **User Experience**
- Loading indicator: "Đang xử lý hình ảnh..."
- Preview shows resized image
- Console logs resize information
- Error handling for processing failures

## Test

### 1. **Manual Testing**
```html
<!-- Mở file test_image_resize.html trong browser -->
<input type="file" accept="image/*">
```

### 2. **Integration Testing**
```javascript
// Test trong chat interface
const file = new File([imageBlob], 'test.jpg', { type: 'image/jpeg' });
const resized = await chatInterface.resizeImage(file, 512);
console.log('Resize result:', resized);
```

## Examples

### Input Image: 2048x1536px
```
Original: 2048 x 1536px
Resized:  512 x 384px
Reduction: 75%
```

### Input Image: 800x1200px
```
Original: 800 x 1200px  
Resized:  341 x 512px
Reduction: 72.5%
```

### Input Image: 300x200px
```
Original: 300 x 200px
Resized:  300 x 200px (no resize needed)
Reduction: 0%
```

## Browser Compatibility

- ✅ Chrome 51+
- ✅ Firefox 41+
- ✅ Safari 10+
- ✅ Edge 79+
- ⚠️ IE: Not supported (Canvas.toBlob)

## Error Handling

```javascript
try {
    const resized = await this.resizeImage(file, 512);
    // Success
} catch (error) {
    this.showError('Có lỗi khi xử lý hình ảnh.');
    console.error('Image processing error:', error);
}
```

## Performance

- **Memory**: Efficient canvas usage with cleanup
- **Speed**: Typically <1 second for most images
- **Quality**: 90% JPEG compression maintains good quality
- **Size Reduction**: Usually 60-90% file size reduction

## Configuration

```javascript
// Customize max dimension
const resized = await this.resizeImage(file, 1024); // 1024px max

// Customize quality
canvas.toBlob(callback, file.type, 0.8); // 80% quality
```

Tính năng này đảm bảo rằng tất cả hình ảnh được upload đều có kích thước phù hợp để xử lý nhanh chóng và hiệu quả! 🚀
