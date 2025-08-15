class ChatInterface {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.imageButton = document.getElementById('imageButton');
        this.imageInput = document.getElementById('imageInput');
        this.imagePreview = document.getElementById('imagePreview');
        this.previewImage = document.getElementById('previewImage');
        this.removeImage = document.getElementById('removeImage');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        
        this.currentImageData = null;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Send message
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Image handling
        this.imageButton.addEventListener('click', () => this.imageInput.click());
        this.imageInput.addEventListener('change', (e) => this.handleImageSelect(e));
        this.removeImage.addEventListener('click', () => this.clearImage());
        
        // Input validation
        this.messageInput.addEventListener('input', () => this.updateSendButton());
    }
    
    updateSendButton() {
        const hasMessage = this.messageInput.value.trim().length > 0;
        const hasImage = this.currentImageData !== null && this.currentImageData.data;
        this.sendButton.disabled = !hasMessage && !hasImage;
    }
    
    async handleImageSelect(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showError('Vui lòng chọn file hình ảnh hợp lệ.');
            return;
        }
        
        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            this.showError('File hình ảnh quá lớn. Vui lòng chọn file nhỏ hơn 5MB.');
            return;
        }
        
        try {
            const base64Data = await this.convertFileToBase64(file);
            this.currentImageData = {
                data: base64Data,
                name: file.name,
                type: file.type
            };
            
            // Show preview
            this.previewImage.src = `data:${file.type};base64,${base64Data}`;
            this.imagePreview.style.display = 'flex';
            
            this.updateSendButton();
        } catch (error) {
            this.showError('Có lỗi khi xử lý hình ảnh.');
            console.error('Image processing error:', error);
        }
    }
    
    convertFileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
    
    clearImage() {
        this.currentImageData = null;
        this.imagePreview.style.display = 'none';
        this.imageInput.value = '';
        this.updateSendButton();
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        const hasImage = this.currentImageData !== null && this.currentImageData.data;
        
        if (!message && !hasImage) return;
        
        // Store image data before clearing
        const imageDataToSend = hasImage ? this.currentImageData : null;
        
        // Add user message to chat
        this.addMessage(message || '[Hình ảnh]', 'user', imageDataToSend);
        
        // Clear input
        this.messageInput.value = '';
        this.clearImage();
        this.updateSendButton();
        
        try {
            this.showLoading(true, 'Đang xử lý tin nhắn...');
            
            const requestData = {
                message: message,
                image_data: imageDataToSend ? imageDataToSend.data : null,
                image_type: imageDataToSend ? imageDataToSend.type : null
            };
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.addMessage(data.response, 'bot');
            } else {
                this.showError(data.message || 'Có lỗi xảy ra khi xử lý tin nhắn.');
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            this.showError('Có lỗi khi gửi tin nhắn. Vui lòng thử lại.');
        } finally {
            this.showLoading(false);
        }
    }
    
    addMessage(content, sender, imageData = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Add image if present
        if (imageData) {
            const imageContainer = document.createElement('div');
            imageContainer.className = 'message-image';
            const img = document.createElement('img');
            img.src = `data:${imageData.type};base64,${imageData.data}`;
            img.alt = 'Uploaded image';
            imageContainer.appendChild(img);
            messageContent.appendChild(imageContainer);
        }
        
        // Process and add text content
        if (content) {
            messageContent.innerHTML += this.processMessageContent(content);
        }
        
        messageDiv.appendChild(messageContent);
        
        // Add TTS button for bot messages
        if (sender === 'bot' && content) {
            const ttsButton = document.createElement('button');
            ttsButton.innerHTML = '<i class="fas fa-volume-up"></i>';
            ttsButton.className = 'tts-button';
            ttsButton.title = 'Phát âm';
            ttsButton.onclick = () => this.playTTS(content);
            messageDiv.appendChild(ttsButton);
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    processMessageContent(content) {
        // Enhanced content processing for better display
        let processedContent = content;
        
        // Convert markdown-style links to HTML with special styling for maps
        processedContent = processedContent.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
            if (url.includes('maps.google.com')) {
                return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="maps-link">${text}</a>`;
            }
            return `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}</a>`;
        });
        
        // Convert **bold** text to <strong>
        processedContent = processedContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert *italic* text to <em>
        processedContent = processedContent.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert line breaks to <br> tags
        processedContent = processedContent.replace(/\n/g, '<br>');
        
        // Highlight restaurant/location names (words ending with specific Vietnamese terms)
        processedContent = processedContent.replace(/((?:[A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]+(?:quán|nhà hàng|chùa|đền|hồ|phố|đường|cầu|tháp|công viên)[a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ\s]*)|([A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ\s]+))/g, '<strong>$1$2</strong>');
        
        // Create structured list for numbered items
        processedContent = processedContent.replace(/(\d+\.\s+)([^\n\d]+)/g, (match, number, content) => {
            return `<div class="numbered-item"><span class="number">${number}</span><span class="content">${content}</span></div>`;
        });
        
        // Wrap addresses in special styling with map button only for specific addresses
        processedContent = processedContent.replace(/(Địa chỉ:\s*)([^\n<]+)/g, (match, label, address) => {
            const addressInfo = `<div class="address-info"><i class="fas fa-map-marker-alt"></i> <span class="address-label">${label}</span><span class="address-text">${address}</span>`;
            
            // Only show map button for specific addresses (containing street numbers, district info, etc.)
            if (this.isSpecificAddress(address)) {
                return addressInfo + `<button class="map-button" onclick="window.chatInterface.searchOnMap('${address}')" title="Xem trên bản đồ"><i class="fas fa-map-marked-alt"></i></button></div>`;
            }
            return addressInfo + '</div>';
        });
        
        // Highlight special features or characteristics
        processedContent = processedContent.replace(/(Đặc sản:|Đặc điểm:|Nổi tiếng:|Hoạt động:|Giờ mở cửa:)([^\n]+)/g, 
            '<div class="feature-info"><span class="feature-label">$1</span><span class="feature-text">$2</span></div>');
        
        return processedContent;
    }
    
    // Check if an address is specific enough to warrant a map button
    isSpecificAddress(address) {
        const specificPatterns = [
            /\d+\/\d+/,  // Street numbers like 123/45
            /\d+\s+[A-Za-zÀ-ỹ]+/,  // Number + street name
            /số\s*\d+/i,  // "số 123"
            /(quận|huyện|thành phố|tp\.|q\.|p\.)[\s\d]/i,  // District/city info
            /(phường|xã)[\s\w]+/i,  // Ward info
            /\d{5,}/,  // Postal codes
            /(đường|phố|ngõ|hẻm)\s+[A-Za-zÀ-ỹ\s]+/i  // Street types with names
        ];
        
        // Check if address contains specific location indicators
        return specificPatterns.some(pattern => pattern.test(address));
    }
    
    // Search address on Google Maps
    searchOnMap(address) {
        const encodedAddress = encodeURIComponent(address);
        const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodedAddress}`;
        window.open(mapsUrl, '_blank');
    }
    
    async playTTS(text) {
        try {
            this.showLoading(true, 'Đang tạo âm thanh...');
            
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });
            
            const data = await response.json();
            
            if (data.status === 'success' && data.audio_data) {
                // Convert base64 to audio blob
                const audioData = atob(data.audio_data);
                const audioArray = new Uint8Array(audioData.length);
                for (let i = 0; i < audioData.length; i++) {
                    audioArray[i] = audioData.charCodeAt(i);
                }
                
                const audioBlob = new Blob([audioArray], { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                
                // Play audio
                const audio = new Audio(audioUrl);
                audio.play().catch(error => {
                    console.error('Audio play error:', error);
                    this.showError('Không thể phát âm thanh.');
                });
                
                // Clean up URL after playing
                audio.addEventListener('ended', () => {
                    URL.revokeObjectURL(audioUrl);
                });
                
            } else {
                this.showError('Không thể tạo âm thanh cho tin nhắn này.');
            }
            
        } catch (error) {
            console.error('TTS error:', error);
            this.showError('Có lỗi khi tạo âm thanh.');
        } finally {
            this.showLoading(false);
        }
    }
    
    showLoading(show, message = 'Đang xử lý...') {
        if (show) {
            const loadingText = this.loadingOverlay.querySelector('p');
            if (loadingText) {
                loadingText.textContent = message;
            }
            this.loadingOverlay.style.display = 'flex';
        } else {
            this.loadingOverlay.style.display = 'none';
        }
    }
    
    showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add to page
        document.body.appendChild(errorDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Initialize chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatInterface = new ChatInterface();
});