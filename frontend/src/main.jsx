import { StrictMode, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { useAuthStore } from './store/authStore'

function AuthHydrator({ children }) {
  useEffect(() => {
    useAuthStore.getState().hydrate();
  }, []);
  return children;
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthHydrator>
      <App />
    </AuthHydrator>
  </StrictMode>,
)
