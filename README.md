# Do_an_ca_nhan_mon_AI
# 1. Giới thiệu bài toán 8_puzzle
Bài toán 8-puzzle (hay còn gọi là bài toán Ta-canh)

Một bảng 3×3 với các ô trong đó có số từ 1 ->8 và 1 ô trống, các ô được đặt ở các vị trí ngẫu nhiên, ô trống và ô số có thể đổi chỗ cho nhau, tìm cách di chuyển các ô sao cho các con số về đúng thứ tự, bài toán đặt ra ở đây là tìm phương án tối ưu sao cho số lần di chuyển là ít nhất.

Các thành phần chính của bài toán tìm kiếm và giải pháp

+ Trạng thái ban đầu
    - Một lưới 3x3 với 8 số từ 1 đến 8 và một ô trống (0), đại diện cho trạng thái khởi đầu của        bài toán ([[1 2 3], [0 5 6], [4 7 8]]).
+ Trạng thái mục tiêu
    - Lưới 3x3 với thứ tự số từ 1 đến 8 và ô trống ở vị trí cuối cùng ([[1 2 3], [4 5 6], [7 8 0]]).
+ Không gian trạng thái
    - Tập hợp tất cả các cấu hình có thể của lưới 3x3 hay các cách sắp xếp cụ thể vị trí các ô.
+ Hành động
    - Di chuyển ô trống lên, xuống, trái, phải để hoán đổi với ô số liền kề.
+ Chi phí
    - Mỗi bước di chuyển có chi phí bằng 1, vì bài toán ưu tiên tìm đường đi ngắn nhất.
+ Giải pháp
    - Dãy các trạng thái từ trạng thái ban đầu đến trạng thái mục tiêu, được tạo ra bởi các thuật toán tìm kiếm không có thông tin BFS, DFS, UCS, và IDS.

# 2. Nội dung

## 2.1. Nhóm thuật toán tìm kiếm không có thông tin (Uninformed Search Algorithms)

### 2.1.1. BFS
BFS là thuật toán duyệt đồ thị hoặc cây theo chiều rộng, tức là nó sẽ duyệt hết tất cả các đỉnh ở một mức (level) trước khi chuyển sang mức tiếp theo.
+ Cấu trúc dữ liệu sử dụng trong BFS
  - Hàng đợi(Queue): dùng để lưu các đỉnh cần duyệt tiếp theo.
  - Tập hợp hoặc đánh dấu (visited): để tránh duyệt lại đỉnh đã thăm.
    (gif/BFS.gif)
  
### 2.1.2. DFS
DFS là thuật toán duyệt đồ thị hoặc cây theo chiều sâu – tức là nó sẽ đi sâu theo từng nhánh trước khi quay lại và duyệt các nhánh còn lại.
+ Cấu trúc dữ liệu sử dụng trong DFS
  - Ngăn xếp(Stack): DFS bản chất là đi sâu xuống từng nhánh → sử dụng ngăn xếp (stack) để lưu các đỉnh chờ được khám phá.
  - Tập hợp các visited để tránh lặp vô hạn (đặc biệt trong đồ thị có chu trình), cần lưu lại các đỉnh đã thăm:
      - Set (tập hợp): Dễ sử dụng, truy cập nhanh O(1)
      - Mảng đánh dấu (boolean array): Dùng khi đỉnh là số nguyên (0 → n-1)
### 2.1.3. IDS (Iterative Deepening Search)
IDS (Iterative Deepening Search – Tìm kiếm mở rộng lặp) là sự kết hợp giữa DFS và BFS. Nó thực hiện nhiều lần DFS với độ sâu giới hạn, tăng dần theo từng bước.
Đây là thuật toán tìm kiếm theo chiều sâu có giới hạn, lặp đi lặp lại với giới hạn độ sâu tăng dần (depth limit = 0 → 1 → 2 → ...), cho đến khi tìm thấy lời giải.
+ Cấu trúc dữ liệu sử dụng trong IDS
  - Call Stack (ngăn xếp hàm): khi dùng DFS đệ quy trong mỗi vòng lặp giới hạn độ sâu
  - Tập hợp/array đánh dấu (visited): giúp tránh lặp đỉnh (nếu cần) – thường dùng trong đồ thị
  - Vòng lặp ngoài (for depth in range(...)): kiểm soát giới hạn độ sâu của DFS
### 2.1.4. UCS (Uniform-Cost Search)
UCS (Uniform Cost Search – Tìm kiếm theo chi phí đồng nhất) là một thuật toán tìm kiếm trên đồ thị/cây giống như BFS, nhưng thay vì duyệt theo mức, nó duyệt theo chi phí đường đi nhỏ nhất từ gốc đến đỉnh hiện tại.
+ Cấu trúc dữ liệu sử dụng trong UCS
  - Priority Queue (heap): luôn chọn đường đi có chi phí thấp nhất để mở rộng tiếp theo
  - Tập visited / closed set: đánh dấu các đỉnh đã xử lý để tránh lặp lại
  - Danh sách kề: biểu diễn đồ thị và chi phí cạnh giữa các đỉnh
  - Tuple (chi phí, đỉnh): gói thông tin cần thiết cho priority queue

## 2.2. Nhóm thuật toán tìm kiếm có thông tin (Informed Search Algorithms)
  
  
