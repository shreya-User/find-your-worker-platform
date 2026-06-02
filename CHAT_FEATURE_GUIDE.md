# Chat Feature Guide - Find My Worker

## 🎉 Chat Feature Successfully Implemented!

The chat system allows workers and customers to communicate with each other, even when workers are not available. Workers can also manage their availability for today and tomorrow.

---

## 📍 Where to Find the Chat Feature

### For Customers (Users):

1. **User Dashboard**
   - URL: `http://localhost:5000/user_dashboard`
   - Look for the **"Messages"** card in the Quick Actions bar (indigo/purple card with chat icon)
   - Click to view all your conversations

2. **Service Requests**
   - On your dashboard, find any **accepted** service request
   - Click the **"Chat"** button (green button) next to "Track Service"
   - This opens a chat with the assigned worker

3. **Browse Services Page**
   - When browsing workers, you can click on a worker's profile
   - From there, you can initiate a chat

4. **Direct Chat Link**
   - URL format: `http://localhost:5000/chat/<worker_id>`
   - Example: `http://localhost:5000/chat/1`

5. **Conversations List**
   - URL: `http://localhost:5000/conversations`
   - View all your active conversations with workers
   - Shows unread message counts
   - Auto-refreshes every 5 seconds

### For Workers:

1. **Worker Dashboard**
   - URL: `http://localhost:5000/worker_dashboard`
   - Look for **"Messages"** in the Quick Actions sidebar
   - Click to view all conversations with customers

2. **Pending Requests**
   - On your dashboard, find any pending service request
   - Click the **"Chat"** button (blue button) next to Accept/Decline
   - This opens a chat with the customer who made the request

3. **Manage Availability**
   - URL: `http://localhost:5000/manage-availability`
   - Set your availability for **Today** and **Tomorrow**
   - Set start and end times
   - Customers can see your availability when chatting

4. **Direct Chat Link**
   - URL format: `http://localhost:5000/chat/customer/<user_id>`
   - Example: `http://localhost:5000/chat/customer/1`

5. **Conversations List**
   - URL: `http://localhost:5000/conversations`
   - View all your active conversations with customers
   - Shows unread message counts

---

## ✨ Features

### Chat Features:
- ✅ Real-time messaging (polls every 3 seconds)
- ✅ Message history
- ✅ Unread message indicators
- ✅ Works even when worker is unavailable
- ✅ Auto-scroll to latest messages
- ✅ Message timestamps
- ✅ Conversation list with last message preview

### Availability Management:
- ✅ Set availability for Today
- ✅ Set availability for Tomorrow
- ✅ Set custom time slots (start/end time)
- ✅ Toggle availability on/off
- ✅ Customers can see availability status
- ✅ Availability shown in chat interface

---

## 🗄️ Database Tables Added

### 1. `chat_conversations`
- Links users and workers
- Tracks last message time
- Can be linked to service requests

### 2. `chat_messages`
- Stores all chat messages
- Tracks sender type (user/worker)
- Read/unread status
- Timestamps

### 3. `worker_availability`
- Stores worker availability for specific dates
- Start and end times
- Today and tomorrow tracking

---

## 🔄 How It Works

### Starting a Chat (Customer):
1. Go to User Dashboard
2. Find an accepted service request
3. Click "Chat" button
4. Or browse workers and click "Chat" on their profile

### Starting a Chat (Worker):
1. Go to Worker Dashboard
2. Find a pending or accepted service request
3. Click "Chat" button
4. Or go to Messages to see all conversations

### Managing Availability (Worker):
1. Go to Worker Dashboard
2. Click "Manage Availability" in Quick Actions
3. Toggle availability for Today/Tomorrow
4. Set time slots if available
5. Click "Save Availability"

---

## 📱 User Interface

### Chat Interface:
- **Header**: Shows other person's name and details
- **Messages Area**: Scrollable message history
- **Input Box**: Type and send messages
- **Availability Info**: Shows worker's availability (for customers)

### Availability Management:
- **Today Section**: Blue background, toggle and time slots
- **Tomorrow Section**: Green background, toggle and time slots
- **Save Button**: Updates availability in database

---

## 🔧 Technical Details

### Routes Added:
- `/chat/<worker_id>` - Customer chat with worker
- `/chat/customer/<user_id>` - Worker chat with customer
- `/api/send-message` - Send a chat message (POST)
- `/api/get-messages/<conversation_id>` - Get messages (GET)
- `/api/conversations` - Get all conversations (GET)
- `/conversations` - Conversations list page
- `/manage-availability` - Manage worker availability (GET/POST)
- `/api/check-availability/<worker_id>` - Check worker availability (GET)

### Real-time Updates:
- Messages poll every 3 seconds
- Conversations list auto-refreshes every 5 seconds
- Availability updates immediately

---

## 🧪 Testing the Feature

### Test as Customer:
1. Login as a user
2. Go to User Dashboard
3. Click "Messages" card
4. Or find an accepted service request and click "Chat"
5. Send a message
6. Check if it appears in the chat

### Test as Worker:
1. Login as a worker
2. Go to Worker Dashboard
3. Click "Manage Availability"
4. Set availability for today and tomorrow
5. Go to Messages or click "Chat" on a service request
6. Send a message to customer
7. Check availability is shown to customers

---

## 📝 Notes

1. **Chat works even when unavailable**: Workers can chat with customers even if they mark themselves as unavailable. Availability only affects when customers can see you're free.

2. **Auto-refresh**: The chat interface automatically checks for new messages every 3 seconds. This is a simple polling approach. For production, consider WebSockets for real-time updates.

3. **Conversations**: A conversation is automatically created when you first chat with someone. It's linked to service requests if available.

4. **Availability**: Workers should update their availability daily. The system tracks today and tomorrow specifically.

5. **Unread Messages**: The system tracks unread messages and shows badges in the conversations list.

---

## 🚀 Future Enhancements

Possible improvements:
- WebSocket support for real-time messaging
- File/image sharing
- Typing indicators
- Message delivery status
- Push notifications
- Chat search functionality
- Group chats for multiple workers/customers

---

## ✅ Status

**Feature Status**: ✅ **Fully Implemented and Ready to Use**

All chat functionality is working:
- ✅ Customer-to-worker chat
- ✅ Worker-to-customer chat
- ✅ Availability management
- ✅ Message history
- ✅ Unread indicators
- ✅ Real-time updates (polling)

---

**Enjoy your new chat feature!** 🎊

For any issues or questions, check the code comments or database schema.
