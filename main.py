# main.py

import cv2
import numpy as np
import os
from hand_tracking_module import HandDetector
from gesture_recognition_module import GestureRecognizer

def main():
    # --- KHỞI TẠO CÁC THAM SỐ ---
    brush_thickness = 15
    draw_color = (0, 0, 255) # Mặc định là màu đỏ (BGR)
    
    # Tọa độ điểm vẽ trước đó
    xp, yp = 0, 0

    # --- KHỞI TẠO CAMERA ---
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Lỗi: Không thể mở camera.")
        return
    cap.set(3, 1280) # Chiều rộng
    cap.set(4, 720)  # Chiều cao

    # --- KHỞI TẠO CÁC MODULE ---
    detector = HandDetector(min_detection_confidence=0.85, max_num_hands=1)
    recognizer = GestureRecognizer()

    # Tạo một canvas ảo để vẽ (phông nền đen)
    img_canvas = np.zeros((720, 1280, 3), np.uint8)

    # --- VÒNG LẶP CHÍNH CỦA ỨNG DỤNG ---
    while True:
        success, img = cap.read()
        if not success:
            print("Lỗi: Không đọc được khung hình từ camera.")
            break
        
        # Lật ảnh để có hiệu ứng gương
        img = cv2.flip(img, 1)

        # 1. Tìm bàn tay và các điểm mốc
        img = detector.find_hands(img, draw=False)
        lm_list = detector.find_position(img, draw=False)

        if len(lm_list) != 0:
            # Lấy tọa độ đầu ngón trỏ (ID 8)
            x1, y1 = lm_list[8][1:]

            # 2. Nhận diện cử chỉ (các ngón tay gập hay duỗi)
            finger_states = recognizer.get_finger_states(lm_list)
            
            # 3. Xử lý cử chỉ
            if finger_states:
                # Cử chỉ 1: Xóa canvas (Nắm tay - tất cả các ngón gập)
                if finger_states == [0, 0, 0, 0, 0]:
                    # Reset lại canvas thành màu đen
                    img_canvas = np.zeros((720, 1280, 3), np.uint8)
                    xp, yp = 0, 0 # Reset điểm vẽ cuối cùng

                # Cử chỉ 2: Vẽ (Ngón trỏ duỗi, ngón giữa gập)
                elif finger_states[1] and not finger_states[2]:
                    cv2.circle(img, (x1, y1), 15, draw_color, cv2.FILLED)
                    
                    # Bắt đầu vẽ khi vào chế độ
                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1
                    
                    # Vẽ đường thẳng từ điểm cũ đến điểm mới
                    cv2.line(img_canvas, (xp, yp), (x1, y1), draw_color, brush_thickness)
                    
                    # Cập nhật lại điểm cũ
                    xp, yp = x1, y1
                
                # Các cử chỉ khác: Reset điểm vẽ để không tạo ra đường nối bất ngờ
                else:
                    xp, yp = 0, 0

        # --- KẾT HỢP HÌNH ẢNH ĐỂ HIỂN THỊ ---
        img_gray = cv2.cvtColor(img_canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, img_inv)
        img = cv2.bitwise_or(img, img_canvas)

        # Hiển thị ảnh kết quả
        cv2.imshow("Virtual Painter", img)

        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()