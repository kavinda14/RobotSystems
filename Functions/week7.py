from ColorTracking import *

class Perception:
    def __init__(self, img):
        global roi
        global rect
        global count
        global track
        global get_roi
        global center_list
        global __isRunning
        global unreachable
        global detect_color
        global action_finish
        global rotation_angle
        global last_x, last_y
        global world_X, world_Y
        global world_x, world_y
        global start_count_t1, t1
        global start_pick_up, first_move

        self.img = img

    def _modify_img(self):
        img_copy = self.img.copy()
        img_h, img_w = self.img.shape[:2]
        cv2.line(self.img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(self.img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

        if not __isRunning:
            return self.img

        frame_resize = cv2.resize(img_copy, size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        #如果检测到某个区域有识别到的物体，则一直检测该区域直到没有为止
        # If a region is detected with a recognized object, the region is detected until it is not
        if get_roi and start_pick_up:
            get_roi = False
            frame_gb = getMaskROI(frame_gb, roi, size)

        # 将图像转换到LAB空间 Convert images to LAB space
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)

        return frame_lab

    def _process_contours(self):
        detect_color = i
        # 对原图像和掩模进行位运算 Bitwise operation of the original image and mask
        frame_mask = cv2.inRange(
            frame_lab, color_range[detect_color][0], color_range[detect_color][1])
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones(
            (6, 6), np.uint8))  # 开运算 Open computing
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones(
            (6, 6), np.uint8))  # 闭运算 Closed operations
        contours = cv2.findContours(
            closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # 找出轮廓 Find the outline
        areaMaxContour, area_max = getAreaMaxContour(
            contours)  # 找出最大轮廓 Find the maximum profile

        return areaMaxContour, area_max
    
    def process_img(self):
        frame_lab = self._modify_img()
        area_max = 0
        areaMaxContour = 0
        if not start_pick_up:
            for i in color_range:
                if i in __target_color:
                    areaMaxContour, area_max = self._process_contours()
            if area_max > 2500:  # 有找到最大面积 Have found the maximum area
                rect = cv2.minAreaRect(areaMaxContour)
                box = np.int0(cv2.boxPoints(rect))

                roi = getROI(box)  # 获取roi区域 Get roi area
                get_roi = True

                # 获取木块中心坐标 Get the coordinates of the center of the block
                img_centerx, img_centery = getCenter(
                    rect, roi, size, square_length)
                # 转换为现实世界坐标 Convert to real-world coordinates
                world_x, world_y = convertCoordinate(
                    img_centerx, img_centery, size)

                cv2.drawContours(self.img, [box], -1, range_rgb[detect_color], 2)
                cv2.putText(self.img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[detect_color], 1)  # 绘制中心点 Plotting the center point
                # 对比上次坐标来判断是否移动 Compare the last coordinate to determine if it is moving
                distance = math.sqrt(
                    pow(world_x - last_x, 2) + pow(world_y - last_y, 2))
                last_x, last_y = world_x, world_y
                track = True
                #print(count,distance)
                # 累计判断 Cumulative judgment
                if action_finish:
                    if distance < 0.3:
                        center_list.extend((world_x, world_y))
                        count += 1
                        if start_count_t1:
                            start_count_t1 = False
                            t1 = time.time()
                        if time.time() - t1 > 1.5:
                            rotation_angle = rect[2]
                            start_count_t1 = True
                            world_X, world_Y = np.mean(
                                np.array(center_list).reshape(count, 2), axis=0)
                            count = 0
                            center_list = []
                            start_pick_up = True
                    else:
                        t1 = time.time()
                        start_count_t1 = True
                        count = 0
                        center_list = []
            
        return self.img
    


