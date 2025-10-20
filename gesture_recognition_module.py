# gesture_recognition_module.py

class GestureRecognizer():
    """
    Lớp để nhận diện các cử chỉ đơn giản từ các điểm mốc của bàn tay.
    """
    def __init__(self):
        # ID của các điểm mốc là đầu ngón tay
        # Theo thứ tự: Ngón cái, trỏ, giữa, áp út, út
        self.tip_ids = [4, 8, 12, 16, 20]

    def get_finger_states(self, lm_list):
        """
        Xác định trạng thái (gập/duỗi) của các ngón tay.
        :param lm_list: Danh sách 21 điểm mốc với id và tọa độ (x, y).
        :return: Một danh sách 5 phần tử, mỗi phần tử là 1 (duỗi) hoặc 0 (gập).
        """
        if len(lm_list) == 0:
            return [] # Trả về danh sách rỗng nếu không có tay

        finger_states =[]

        # --- Logic cho Ngón cái ---
        # So sánh tọa độ x của đầu ngón cái (ID 4) và khớp gần nhất (ID 3).
        # Vì ảnh đã lật, với bàn tay phải, x của đầu ngón tay sẽ nhỏ hơn khi duỗi.
        # Lưu ý: Logic này giả định là bàn tay phải.
        if lm_list[self.tip_ids[0]][1] < lm_list[self.tip_ids[0] - 1][1]:
            finger_states.append(1) # Duỗi
        else:
            finger_states.append(0) # Gập

        # --- Logic cho 4 ngón còn lại ---
        # So sánh tọa độ y của đầu ngón tay và khớp bên dưới nó (cách 2 điểm mốc).
        # Vì gốc tọa độ (0,0) ở góc trên bên trái, y nhỏ hơn nghĩa là điểm đó ở cao hơn.
        for id in range(1, 5):
            # Ví dụ: so sánh đầu ngón trỏ (ID 8) với khớp bên dưới (ID 6)
            if lm_list[self.tip_ids[id]][2] < lm_list[self.tip_ids[id] - 2][2]:
                finger_states.append(1) # Duỗi
            else:
                finger_states.append(0) # Gập
        
        return finger_states
