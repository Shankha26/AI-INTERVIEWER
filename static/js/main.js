// PrepAI Pro Master Client JS

document.addEventListener('DOMContentLoaded', () => {
    // 1. Dark / Light Mode Switcher
    const themeToggleBtn = document.getElementById('themeToggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Set initial theme
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeUI(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            let theme = document.documentElement.getAttribute('data-theme');
            let newTheme = theme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeUI(newTheme);
        });
    }

    function updateThemeUI(theme) {
        if (!themeToggleBtn) return;
        const icon = themeToggleBtn.querySelector('i');
        const text = themeToggleBtn.querySelector('.theme-text');
        
        if (theme === 'dark') {
            if (icon) icon.className = 'bi bi-sun-fill';
            if (text) text.textContent = 'Light Mode';
        } else {
            if (icon) icon.className = 'bi bi-moon-stars-fill';
            if (text) text.textContent = 'Dark Mode';
        }
    }

    // 2. Auto-fade Flash Alerts
    const alerts = document.querySelectorAll('.alert-animated');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.6s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 600);
        }, 5000);
    });
    
    // 3. Sidebar Toggle for Mobile View
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }
});

// 4. Voice Recording & HTML5 Speech Recognition Controller
class InterviewRecorder {
    constructor(videoElementId, visualizerCanvasId, questionIdx, onTranscriptWord) {
        this.videoElement = document.getElementById(videoElementId);
        this.visualizerCanvas = document.getElementById(visualizerCanvasId);
        this.questionIdx = questionIdx;
        this.onTranscriptWord = onTranscriptWord;
        
        this.mediaStream = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.videoChunks = [];
        
        this.recognition = null;
        this.isRecording = false;
        
        // Initialize HTML5 Web Speech API for real-time transcription
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';
        }
    }

    async start() {
        if (this.isRecording) return;
        
        this.audioChunks = [];
        this.videoChunks = [];
        
        try {
            // Request micro and camera access
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: true,
                video: true
            });
            
            // Hook up video display feed
            if (this.videoElement) {
                this.videoElement.srcObject = this.mediaStream;
                this.videoElement.play();
            }
            
            // Set up MediaRecorder
            // Use WebM as standard browser container (plays in HTML5)
            let options = { mimeType: 'video/webm;codecs=vp8,opus' };
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options = { mimeType: 'video/webm' };
            }
            
            this.mediaRecorder = new MediaRecorder(this.mediaStream, options);
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) {
                    this.videoChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.start(1000); // chunk size 1s
            
            // Real-time audio waveform visualizer setup (canvas)
            this._setupVisualizer();
            
            // Start Speech-To-Text
            if (this.recognition) {
                this.recognition.onresult = (event) => {
                    let fullTranscript = '';
                    for (let i = 0; i < event.results.length; ++i) {
                        if (event.results[i].isFinal) {
                            fullTranscript += event.results[i][0].transcript;
                        }
                    }
                    if (this.onTranscriptWord && fullTranscript) {
                        this.onTranscriptWord(fullTranscript);
                    }
                };
                this.recognition.start();
            }
            
            this.isRecording = true;
            console.log("Webcam and microphone recording started...");
            
        } catch (err) {
            console.error("Error accessing camera/microphone:", err);
            alert("Could not access camera/microphone. Please verify hardware permissions.");
            throw err;
        }
    }

    async stop() {
        if (!this.isRecording) return null;
        
        return new Promise((resolve) => {
            this.mediaRecorder.onstop = async () => {
                // Stop speech-to-text
                if (this.recognition) {
                    this.recognition.stop();
                }
                
                // Stop all tracks on the stream
                if (this.mediaStream) {
                    this.mediaStream.getTracks().forEach(track => track.stop());
                }
                
                // Create Video Blob
                const videoBlob = new Blob(this.videoChunks, { type: 'video/webm' });
                
                // Create Audio-only Blob from tracks if needed (or we can extract from webm backend, 
                // but standard uploader can send the same blob representing combined track and save audio/video)
                const audioBlob = new Blob(this.videoChunks, { type: 'audio/webm' }); 
                
                this.isRecording = false;
                console.log("Recording stopped. Assembled blobs.");
                
                resolve({
                    videoBlob: videoBlob,
                    audioBlob: audioBlob
                });
            };
            
            this.mediaRecorder.stop();
        });
    }

    _setupVisualizer() {
        if (!this.visualizerCanvas || !this.mediaStream) return;
        
        const canvasCtx = this.visualizerCanvas.getContext('2d');
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioCtx.createMediaStreamSource(this.mediaStream);
        const analyser = audioCtx.createAnalyser();
        
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        source.connect(analyser);
        
        const draw = () => {
            if (!this.isRecording) return;
            
            requestAnimationFrame(draw);
            
            analyser.getByteFrequencyData(dataArray);
            
            const width = this.visualizerCanvas.width;
            const height = this.visualizerCanvas.height;
            
            canvasCtx.fillStyle = 'rgba(11, 15, 25, 0.2)';
            canvasCtx.fillRect(0, 0, width, height);
            
            const barWidth = (width / bufferLength) * 2.5;
            let barHeight;
            let x = 0;
            
            for (let i = 0; i < bufferLength; i++) {
                barHeight = dataArray[i] / 2;
                
                // Premium Purple color palette matching theme
                canvasCtx.fillStyle = `rgb(${barHeight + 100}, 102, 241)`;
                canvasCtx.fillRect(x, height - barHeight, barWidth, barHeight);
                
                x += barWidth + 1;
            }
        };
        
        draw();
    }
}
