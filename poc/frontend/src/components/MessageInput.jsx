import { useState } from 'react'

function MessageInput({ onSendMessage, disabled }) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message)
      setMessage('')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-end space-x-3">
      {/* Input field */}
      <div className="flex-1">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={disabled}
          placeholder={disabled ? 'ממתין לתשובה...' : 'הקלד את השאלה המשפטית שלך כאן...'}
          rows={1}
          className={`w-full resize-none rounded-lg border-2 px-4 py-3 text-sm placeholder-secondary-400 transition-colors focus:outline-none ${
            disabled
              ? 'border-secondary-200 bg-secondary-50 text-secondary-400'
              : 'border-secondary-300 bg-white text-secondary-900 focus:border-primary-500'
          }`}
          style={{
            minHeight: '48px',
            maxHeight: '120px',
          }}
          onInput={(e) => {
            // Auto-resize textarea
            e.target.style.height = 'auto'
            e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
          }}
        />
      </div>

      {/* Send button */}
      <button
        type="submit"
        disabled={disabled || !message.trim()}
        className={`flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg transition-colors ${
          disabled || !message.trim()
            ? 'bg-secondary-200 text-secondary-400 cursor-not-allowed'
            : 'bg-primary-500 text-white hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
        }`}
      >
        {disabled ? (
          // Loading spinner
          <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        ) : (
          // Send icon
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        )}
      </button>
    </form>
  )
}

export default MessageInput