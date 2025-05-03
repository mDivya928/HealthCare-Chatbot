const sendBtn = document.getElementById('send-btn');
sendBtn.addEventListener('click', sendMessage);
document.getElementById('user-input')
        .addEventListener('keypress', e => { if (e.key === 'Enter') sendMessage(); });

function sendMessage() {
  const input = document.getElementById('user-input');
  const msg   = input.value.trim();
  if (!msg) return;
  appendMessage('user', msg);
  input.value = '';
  fetch('/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: msg })
  })
    .then(r => r.json())
    .then(data => appendMessage('bot', data.reply))
    .catch(() => appendMessage('bot', "Oops, something went wrong."));
}

function appendMessage(who, text) {
  const box = document.getElementById('chat-box');
  const div = document.createElement('div');
  div.classList.add('message', who);
  div.innerText = text;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}
