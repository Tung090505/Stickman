import json

path = r'C:\File D\Stickman\caveman-story\project.json'
with open(path, 'r', encoding='utf-8') as f:
    p = json.load(f)

p['captions'] = [
    {"start": 0.0, "end": 1.5, "text": "Hãy thử tưởng tượng bạn đang sống..."},
    {"start": 1.5, "end": 3.0, "text": "...trên Trái Đất một triệu năm trước."},
    {"start": 3.0, "end": 5.0, "text": "Khi mặt trời lặn xuống,"},
    {"start": 5.0, "end": 6.8, "text": "bóng tối đen đặc bao trùm."},
    {"start": 6.8, "end": 9.0, "text": "Không điện thoại. Không ánh đèn."},
    {"start": 9.0, "end": 11.5, "text": "Và không hề có một đốm lửa."},
    {"start": 11.5, "end": 14.0, "text": "Màn đêm là cơn ác mộng sinh tử."},
    {"start": 14.0, "end": 17.0, "text": "Trong bóng đêm lạnh lẽo,"},
    {"start": 17.0, "end": 20.0, "text": "thính giác căng thẳng đến nghẹt thở."},
    {"start": 20.0, "end": 23.2, "text": "Xung quanh là hổ răng kiếm,"},
    {"start": 23.2, "end": 26.4, "text": "và những đôi mắt nhìn xuyên bóng tối."},
    {"start": 26.4, "end": 28.5, "text": "Loài người khi ấy rất yếu ớt,"},
    {"start": 28.5, "end": 30.3, "text": "chỉ là con mồi trong đêm."},
    {"start": 30.3, "end": 33.1, "text": "Không có lửa: mùa đông là án tử."},
    {"start": 33.1, "end": 36.5, "text": "Tổ tiên ôm nhau tìm hơi ấm,"},
    {"start": 36.5, "end": 39.9, "text": "nhiều người ngủ thiếp đi vĩnh viễn."},
    {"start": 39.9, "end": 43.5, "text": "Thức ăn thì sao? Không xào nấu."},
    {"start": 43.5, "end": 48.0, "text": "Từ củ dại đến thịt thú đều nhai sống."},
    {"start": 48.0, "end": 52.0, "text": "Nhai từng thớ cơ dai suốt hàng giờ,"},
    {"start": 52.0, "end": 56.4, "text": "dạ dày gồng mình chống vi khuẩn."},
    {"start": 56.4, "end": 60.5, "text": "Bị giam cầm giữa lạnh, tối và thú dữ."},
    {"start": 60.5, "end": 64.2, "text": "Nhưng trong não là một vũ khí phi thường."},
    {"start": 64.2, "end": 67.2, "text": "Sự tò mò và khát vọng sống sót."},
    {"start": 67.2, "end": 70.0, "text": "Họ cần một phép màu lật ngược thế cờ."},
    {"start": 70.0, "end": 72.4, "text": "Một tiếng sét xé toạc không gian!"},
    {"start": 72.4, "end": 74.75, "text": "Mở ra bước ngoặt vĩ đại nhất!"}
]

with open(path, 'w', encoding='utf-8') as f:
    json.dump(p, f, ensure_ascii=False, indent=2)

print('Captions updated!')
