# AI Racing Game

## Mô tả Dự án
AI Racing Game là một dự án kết hợp giữa lập trình game và máy học, đặc biệt là lĩnh vực học tăng cường (Reinforcement Learning). Trong game này, người chơi có thể đua xe tích điểm và so sánh số điểm với một mô hình được huấn luyện sẵn có chức năng tránh chướng ngại vật và đạt được điểm cao nhất có thể.

### Đối tượng chính
- **Người chơi:** Điều khiển xe tránh chướng ngại vật trong môi trường game.
- **AI:** Sử dụng mô hình máy học tăng cường (điển hình là Q-learning) để điểu khiển xe hành động hiệu quả.
- **Giao diện:** Giao diện game 2D đơn giản hiển thị môi trường game cũng như điểm số ở phía người chơi và thông số học máy ở phía Agent.

---

## Cấu trúc thư mục

```plaintext
AI-Racing-Game/
│
├── assets/                 # Tài nguyên game (hình ảnh, âm thanh, v.v.)
│   ├── images/             # Hình ảnh sử dụng trong game
│   ├── sounds/             # Âm thanh trong game
│
├── game/                   # Mã nguồn logic gốc của game, người dùng có thể trải nghiệm gameplay
│
├── tests/                  # Thư mục chứa mã nguồn game tích hợp mô hình học máy, nơi để Agent có thể tự học cách chơi để tối ưu hóa số điểm
│
├── requirements.txt        # Danh sách các thư viện Python cần thiết
```

---

## Cài đặt

1. Clone repo:
   ```bash
   git clone https://github.com/username/RL-Racing.git
   ```
2. Cài đặt các thư viện Python cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

---

