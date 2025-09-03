import { formatDistanceToNow } from 'date-fns'
import { he } from 'date-fns/locale'

function ChatMessage({ message }) {
  const { text, isBot, timestamp, processingTime, isError } = message

  return (
    <div className={`flex ${isBot ? 'justify-start' : 'justify-end'}`}>
      <div className={`max-w-[70%] ${isBot ? 'order-2' : 'order-1'}`}>
        {/* Message bubble */}
        <div
          className={`rounded-2xl px-4 py-3 ${
            isBot
              ? isError
                ? 'bg-red-100 text-red-800 border border-red-200'
                : 'bg-secondary-100 text-secondary-800'
              : 'bg-primary-500 text-white'
          }`}
        >
          {/* Message text */}
          <div className="whitespace-pre-wrap text-sm leading-relaxed">
            {text}
          </div>
          
          {/* Processing time for bot messages */}
          {isBot && processingTime && !isError && (
            <div className="text-xs text-secondary-500 mt-2 opacity-70">
              עובד תוך {processingTime} שניות
            </div>
          )}
        </div>
        
        {/* Timestamp */}
        <div
          className={`text-xs text-secondary-400 mt-1 px-1 ${
            isBot ? 'text-right' : 'text-left'
          }`}
        >
          {formatDistanceToNow(timestamp, { addSuffix: true, locale: he })}
        </div>
      </div>
      
      {/* Avatar */}
      <div className={`flex-shrink-0 ${isBot ? 'order-1 ml-3' : 'order-2 mr-3'}`}>
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isBot
              ? isError
                ? 'bg-red-100 text-red-600'
                : 'bg-primary-100 text-primary-600'
              : 'bg-secondary-600 text-white'
          }`}
        >
          {isBot ? (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </div>
      </div>
    </div>
  )
}

export default ChatMessage