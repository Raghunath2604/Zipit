import streamlit as st
import streamlit.components.v1 as components

def configure_responsive_ui():
    """Configure responsive UI for both mobile and desktop"""
    
    # Responsive CSS for mobile and desktop
    st.markdown("""
    <style>
        /* Mobile-first responsive design */
        .main-container {
            padding: 0.5rem;
        }
        
        /* Desktop styles */
        @media (min-width: 768px) {
            .main-container {
                padding: 2rem;
            }
            
            .desktop-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1rem;
            }
        }
        
        /* Mobile styles */
        @media (max-width: 767px) {
            .stSidebar {
                width: 100% !important;
            }
            
            .mobile-stack {
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }
            
            .metric-card {
                min-height: 80px;
                padding: 1rem;
            }
            
            /* Hide complex charts on mobile */
            .desktop-only {
                display: none;
            }
        }
        
        /* Touch-friendly buttons */
        .stButton > button {
            min-height: 44px;
            font-size: 16px;
        }
        
        /* Responsive navigation */
        .nav-mobile {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            border-top: 1px solid #ddd;
            padding: 0.5rem;
            z-index: 1000;
        }
        
        /* PWA styles */
        .pwa-install {
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1001;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Device detection
    device_type = detect_device()
    st.session_state.device_type = device_type
    
    return device_type

def detect_device():
    """Detect if user is on mobile or desktop"""
    
    # JavaScript to detect device type
    device_detection = """
    <script>
        function detectDevice() {
            const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            const isTablet = /iPad|Android/i.test(navigator.userAgent) && window.innerWidth > 768;
            
            if (isMobile && !isTablet) {
                return 'mobile';
            } else if (isTablet) {
                return 'tablet';
            } else {
                return 'desktop';
            }
        }
        
        const deviceType = detectDevice();
        window.parent.postMessage({type: 'device_detection', device: deviceType}, '*');
    </script>
    """
    
    components.html(device_detection, height=0)
    
    # Default to desktop if detection fails
    return st.session_state.get('detected_device', 'desktop')

def mobile_navigation():
    """Mobile-optimized bottom navigation"""
    
    st.markdown("""
    <div class="nav-mobile">
        <div style="display: flex; justify-content: space-around;">
            <div style="text-align: center;">
                <div>🏠</div>
                <small>Home</small>
            </div>
            <div style="text-align: center;">
                <div>🔧</div>
                <small>Code</small>
            </div>
            <div style="text-align: center;">
                <div>📊</div>
                <small>Data</small>
            </div>
            <div style="text-align: center;">
                <div>🤖</div>
                <small>AutoML</small>
            </div>
            <div style="text-align: center;">
                <div>⚙️</div>
                <small>More</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def pwa_install_prompt():
    """Progressive Web App install prompt"""
    
    pwa_script = """
    <script>
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            
            // Show install button
            const installBtn = document.createElement('button');
            installBtn.innerHTML = '📱 Install App';
            installBtn.className = 'pwa-install';
            installBtn.style.cssText = `
                background: #667eea;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
            `;
            
            installBtn.addEventListener('click', () => {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        console.log('PWA installed');
                    }
                    deferredPrompt = null;
                    installBtn.remove();
                });
            });
            
            document.body.appendChild(installBtn);
        });
    </script>
    """
    
    components.html(pwa_script, height=0)

def adaptive_layout(content_func, mobile_content_func=None):
    """Adaptive layout that changes based on device type"""
    
    device_type = st.session_state.get('device_type', 'desktop')
    
    if device_type == 'mobile' and mobile_content_func:
        mobile_content_func()
    else:
        content_func()

if __name__ == "__main__":
    configure_responsive_ui()