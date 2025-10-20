# hand_tracking_module.py

import cv2
import mediapipe as mp
import time

class HandDetector():
    """
    Lớp để phát hiện và theo dõi bàn tay bằng MediaPipe.
    """
    def __init__(self, static_image_mode=False, max_num_hands=1, 
                 min_detection_confidence=0.7, min_tracking_confidence=0.7):
        """
        Khởi tạo các tham số cho việc nhận diện bàn tay.
        :param static_image_mode: Nếu là True, việc nhận diện sẽ chạy trên mỗi ảnh. 
                                  Nếu là False, detector sẽ cố gắng theo dõi bàn tay.
        :param max_num_hands: Số lượng bàn tay tối đa có thể nhận diện.
        :param min_detection_confidence: Ngưỡng tin cậy tối thiểu để xem một phát hiện là thành công.
        :param min_tracking_confidence: Ngưỡng tin cậy tối thiểu để theo dõi bàn tay.
        """
        self.mode = static_image_mode
        self.max_hands = max_num_hands
        self.detection_con = min_detection_confidence
        self.track_con = min_tracking_confidence

        # Khởi tạo giải pháp Hands của MediaPipe
        self.mp_hands = mp.solutions.hands
        
        # Sửa lỗi tương thích với phiên bản MediaPipe mới
        self.hands = self.mp_hands.Hands(static_image_mode=self.mode, 
                                          max_num_hands=self.max_hands,
                                          min_detection_confidence=self.detection_con, 
                                          min_tracking_confidence=self.track_con)
        
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        """
        Tìm kiếm bàn tay trong một khung hình.
        :param img: Khung hình (ảnh) để tìm kiếm bàn tay.
        :param draw: Cờ để quyết định có vẽ các điểm mốc và đường nối lên ảnh hay không.
        :return: Trả về ảnh đã được xử lý (có thể đã được vẽ lên).
        """
        # Chuyển đổi không gian màu từ BGR sang RGB vì MediaPipe yêu cầu RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        # Kiểm tra xem có bàn tay nào được phát hiện không
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    # Vẽ các điểm mốc và đường nối giữa chúng
                    self.mp_draw.draw_landmarks(img, hand_lms,
                                                self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_position(self, img, hand_no=0, draw=True):
        """
        Trích xuất vị trí (tọa độ pixel) của các điểm mốc.
        :param img: Khung hình đang được xử lý.
        :param hand_no: Chỉ số của bàn tay cần lấy vị trí (mặc định là 0).
        :param draw: Cờ để quyết định có vẽ vòng tròn lên một điểm mốc cụ thể không.
        :return: Danh sách các điểm mốc với id và tọa độ (x, y).
        """
        # === DÒNG 67 ĐÃ SỬA LỖI ===
        # Khởi tạo một danh sách rỗng để chứa tọa độ
        lm_list = []
        
        if self.results.multi_hand_landmarks:
            # Chọn bàn tay cụ thể
            my_hand = self.results.multi_hand_landmarks[hand_no]
            h, w, c = img.shape
            
            # Lặp qua tất cả 21 điểm mốc
            for id, lm in enumerate(my_hand.landmark):
                # Chuyển đổi tọa độ đã chuẩn hóa thành tọa độ pixel
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
                if draw:
                    # Vẽ một vòng tròn tại điểm mốc đầu ngón trỏ để kiểm tra
                    if id == 8:
                        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        return lm_list

def main():
    """
    Hàm chính để chạy thử nghiệm module nhận diện bàn tay.
    """
    p_time = 0
    c_time = 0
    cap = cv2.VideoCapture(0) # Mở webcam

    if not cap.isOpened():
        print("Lỗi: Không thể mở webcam.")
        return
        
    detector = HandDetector()

    while True:
        success, img = cap.read()
        if not success:
            print("Lỗi: Không thể đọc khung hình từ webcam. Đang thoát...")
            break
        
        # Lật ảnh để có hiệu ứng gương
        img = cv2.flip(img, 1)

        # Tìm tay và vẽ lên ảnh
        img = detector.find_hands(img)
        
        # Lấy danh sách vị trí các điểm mốc
        lm_list = detector.find_position(img)
        if len(lm_list)!= 0:
            # In vị trí của đầu ngón trỏ (điểm mốc số 8)
            print(lm_list[1])

        # Tính toán và hiển thị FPS
        c_time = time.time()
        fps = 1 / (c_time - p_time)
        p_time = c_time
        cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        
        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()