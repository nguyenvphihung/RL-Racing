# AI Racing Game

## Mô tả Dự án
AI Racing Game là một dự án kết hợp giữa lập trình game và máy học, đặc biệt là lĩnh vực học tăng cường (Reinforcement Learning). Trong game này, người chơi sẽ đua xe với một mô hình được huấn luyện để tránh chướng ngại vật và đạt được điểm cao nhất có thể.

### Tính năng chính
- **Người chơi:** Điều khiển xe trênh chướng ngại vật trong môi trường game.
- **AI:** Sử dụng mô hình máy học tăng cường (điển hình là DQN hoặc PPO) để xe AI hành động hiệu quả.
- **Giao diện:** Hiển thị điểm số, so sánh kết quả giữa người chơi và AI.

---

## Cấu trúc thư mục

```plaintext
AI-Racing-Game/
│
├── assets/                 # Tài nguyên game (hình ảnh, âm thanh, v.v.)
│   ├── images/             # Hình ảnh sử dụng trong game
│   ├── sounds/             # Âm thanh trong game
│   └── fonts/              # Phông chữ sử dụng trong game
│
├── game/                   # Mã nguồn logic của game
│   ├── main.py             # Tệp chính để chạy game
│   ├── settings.py         # Cấu hình game (kích thước cửa sổ, v.v.)
│   ├── player.py           # Lớp điều khiển xe người chơi
│   ├── ai_player.py        # Lớp điều khiển xe AI
│   └── obstacle.py         # Lớp quản lý chướng ngại vật
│
├── ai/                     # Mã nguồn cho AI và mô hình máy học
│   ├── model_training.py   # Tập huấn mô hình AI
│   ├── agent.py            # Lớp quản lý agent AI
│   ├── environment.py      # Môi trường game để AI tương tác
│   ├── trained_model/      # Lưu trữ mô hình đã huấn luyện
│   └── hyperparameters.json # File cấu hình hyperparameters
│
│
├── tests/                  # Thư mục chứa các bài kiểm thử
│   ├── test_game.py        # Kiểm thử logic của game
│   ├── test_ai.py          # Kiểm thử AI agent
│   └── test_environment.py # Kiểm thử môi trường tương tác của AI
│
├── requirements.txt        # Danh sách các thư viện Python cần thiết
├── LICENSE                 # Bản quyền dự án
└── .gitignore              # Tệp cấu hình Git
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

