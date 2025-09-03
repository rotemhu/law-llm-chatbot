import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import ChatMessage from './components/ChatMessage'
import MessageInput from './components/MessageInput'
import TypingIndicator from './components/TypingIndicator'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'שלום! אני עוזר משפטי מבוסס בינה מלאכותית. איך אוכל לעזור לך היום?',
      isBot: true,
      timestamp: new Date()
    }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  const handleSendMessage = async (messageText) => {
    if (!messageText.trim()) return

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: messageText,
      isBot: false,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/chat`, {
        user_prompt: messageText,
        chat_id: `chat_${Date.now()}`,
        max_tokens: 1000,
        temperature: 0.7
      })

      // Add bot response
      const botMessage = {
        id: Date.now() + 1,
        text: response.data.answer,
        isBot: true,
        timestamp: new Date(),
        processingTime: response.data.processing_time_seconds
      }
      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: 'מצטער, אירעה שגיאה בעת עיבוד השאלה שלך. אנא נסה שוב.',
        isBot: true,
        isError: true,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-secondary-200">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
              <svg 
                className="w-6 h-6 text-white" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" 
                />
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M8 5a2 2 0 012-2h4a2 2 0 012 2v2H8V5z" 
                />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-secondary-900">
                יועץ משפטי
              </h1>
              <p className="text-secondary-600 text-sm">
                בינה מלאכותית למשפט הישראלי
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Chat Area */}
      <main className="max-w-4xl mx-auto px-4 py-6">
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Messages Container */}
          <div className="h-[600px] overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            
            {/* Typing Indicator */}
            {isLoading && <TypingIndicator />}
            
            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-secondary-200 p-4">
            <MessageInput 
              onSendMessage={handleSendMessage} 
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-6 text-center">
          <p className="text-secondary-500 text-sm max-w-2xl mx-auto">
            התשובות המוצגות כאן הן להנחיה בלבד ואינן מהוות ייעוץ משפטי מקצועי. 
            לצורך ייעוץ משפטי מדויק, יש לפנות לעורך דין מוסמך.
          </p>
        </div>
      </main>
    </div>
  )
}

export default App