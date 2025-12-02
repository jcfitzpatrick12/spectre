import React from 'react'

function FriendlyError({
  title = 'Something hiccuped.',
  detail,
  onRetry,
  retryLabel = 'Try again',
  onDismiss,
  dismissLabel = 'Dismiss'
}) {
  return (
    <div className="friendly-error" role="alert">
      <p className="friendly-error-title">{title}</p>
      {detail && <p className="friendly-error-detail">{detail}</p>}
      <div className="friendly-error-actions">
        {onRetry && (
          <button className="refresh-button" onClick={onRetry}>
            {retryLabel}
          </button>
        )}
        {onDismiss && (
          <button className="reset-button" onClick={onDismiss}>
            {dismissLabel}
          </button>
        )}
      </div>
    </div>
  )
}

export default FriendlyError
