// Update unread count badge every 30 seconds
function updateNotificationBadge() {
    fetch('/notifications/unread-count')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('notification-badge');
            badge.textContent = data.count || '';
            badge.style.display = data.count > 0 ? 'inline' : 'none';
        });
}

setInterval(updateNotificationBadge, 30000);
updateNotificationBadge(); // Initial load