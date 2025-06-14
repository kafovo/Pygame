import pygame
import os
import sys
import random
import json

BLUE = (0, 0, 200)
LIGHT_BLUE = (100, 100, 255)

BLACK = (0, 0, 0)
# 初始化Pygame
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
pygame.mixer.init()
hit_e = pygame.mixer.Sound('sound/hit.mp3')
# 定义常量
WIDTH = 1280
HEIGHT = 720
line_h = 160
track_w = 160
track_l = 320
tol = 0
type_dict = {0: 'tap'}
musics = {0: "music/BRAVE：ROAD.mp3",1:'music/GALACTIC WARZONE.mp3'}
scs = {'perfect':100,'good' : 75,'miss':0}
spic = {0:'b0',1:"h0"}
sfile = {0:'charts/BRAVE：ROAD.json',1:"charts/GALACTIC WARZONE.json"}
# 创建屏幕
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AOI Game")
def place(rect,x,y,r = None):
    rect.left = x
    if r:
        rect.right = x
    rect.top = y
# 协助定位轨道
def setx(idx):
    return track_l + idx * track_w

# 加载图片
def load_image(image_name):
    return pygame.image.load(f"images/{image_name}.png").convert_alpha()

# 场景内图片对象处理
class Item:
    def __init__(self, image, x, y, width=None, height=None):
        self.image = load_image(image)
        if width and height:
            self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(left=x, bottom=y)

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        pass

# 字体气泡类
class pop:
    def __init__(self, x, y, image, string, font, size,drac = True):
        self.image = load_image(image)
        self.rect = self.image.get_rect(center=(x, y))
        self.rect.left = x
        self.rect.top = y
        self.s = string  # 内容
        self.fname = font  # 字体名
        self.selected = False  # 交互
        self.size = size
        self.drac = drac
        self.font = pygame.font.Font(font, size) #字体表面实例

    def draw(self):
        color = (255, 0, 0) if self.selected else (255, 255, 255)
        if self.drac:
            screen.blit(self.image, self.rect)
        text_surface = self.font.render(self.s, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def upop(self, pos):
        self.selected = self.rect.collidepoint(pos)

    def update(self, dt):
        pass

# 气泡效果
class Bobble:
    def __init__(self, status, max=200):
        self.on = status
        self.bobbles = []
        self.max = max
        self.spawn_rate = 1  # 生成阈值
        self.colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                       (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                       (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))]

    def create(self):
        return {
            'x': random.randint(0, WIDTH),
            'y': random.randint(HEIGHT - 50, HEIGHT),
            'vx': random.uniform(-0.5, 0.5),  # 水平方向轻微摆动
            'vy': random.uniform(-2, -1),  # 上升速度
            'life': 1.0,
            'size': random.randint(10, 30),  # 粒子大小
            'color': random.choice(self.colors)
        }

    def update(self, dt):
        if not self.on:
            return
        self.colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                       (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                       (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))]
        if len(self.bobbles) < self.max and random.random() < self.spawn_rate:
            self.bobbles.append(self.create())

        for p in self.bobbles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= dt * 0.1

            if p['x'] < 0 or p['x'] > WIDTH:
                p['vx'] *= -0.5
            if p['y'] < 0:
                p['life'] = 0
        self.bobbles = [p for p in self.bobbles if p['life'] > 0]

    def draw(self):
        if not self.on:
            return
        for p in self.bobbles:
            alpha = int(255 * p['life'])
            surf = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                surf,
                (*p['color'], alpha),  # 使用RGBA
                (p['size'], p['size']),
                p['size']
            )
            screen.blit(surf, (int(p['x'] - p['size']), int(p['y'] - p['size'])))

# 场景类
class Scene:
    def __init__(self, image, on, width=None, height=None):
        self.back = load_image(image)
        self.image = load_image(image)
        if width and height:
            self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.back.get_rect()
        self.actors = []
        self.pops = []
        self.bob = Bobble(on)

    def draw(self):
        screen.blit(self.back, self.rect)
        self.bob.draw()
        for i in self.actors:
            i.draw()
        for i in self.pops:
            i.draw()

    def update(self, dt):
        self.bob.update(dt)
        for i in self.actors:
            i.update()
        for i in self.pops:
            i.update(dt)

    def upop(self, pos):
        for i in self.pops:
            i.upop(pos)
    def change(self,image,width = None,height = None):
        self.back = load_image(image)
        self.image = load_image(image)
        if width and height:
            self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.back.get_rect()

# 动画效果文本
class APop(pop):
    def __init__(self, x, y, image, string, font, size, t=2):
        super().__init__(x, y, image, string, font, size,False)
        self.t = t
        self.b = 0
        self.ia = 0  # 初始透明度为0
        self.fa = 255  # 最终透明度为255
        self.color = (255, 255, 255)  # 初始化颜色
        self.alpha = self.ia  # 初始化透明度

    def update(self, dt):
        if self.b < self.t:
            self.b += dt
            alpha = int(self.ia + (self.fa - self.ia) * (self.b / self.t))
            self.color = (0, 0, 0)  # 更新颜色
            self.alpha = alpha
        else:
            self.color = (0, 0, 0)  # 确保最终颜色为白色
            self.alpha = self.fa

    def draw(self):
        lines = self.s.split('\n')
        font = pygame.font.Font(self.fname, self.size)
        y_offset = 0
        for line in lines:
            text = font.render(line, True, self.color)
            text_rect = text.get_rect(center=(self.rect.center[0], self.rect.center[1] + y_offset))
            text.set_alpha(self.alpha)
            screen.blit(text, text_rect)
            y_offset += self.size

    def reset(self):
        self.b = 0
        self.ia = 0  # 初始透明度为0
        self.fa = 255  # 最终透明度为255
        self.color = (255, 255, 255)  # 初始化颜色
        self.alpha = self.ia  # 初始化透明度

# 轨道类
class Track:
    def __init__(self, idx):
        self.id = idx
        self.track = pygame.Rect(setx(idx), 0, track_w, HEIGHT)
        self.notes = []
        self.t = 0.5  # 渐变时间
        self.b = 0  # 已过去的时间
        self.ia = 0  # 初始透明度为0
        self.fa = 255  # 最终透明度为255
        self.alpha = self.ia  # 初始化透明度
        self.isf = False  # 标记轨道是否正在闪烁
        self.fd = 0.2  # 闪烁持续时间
        self.ft = 0  # 闪烁计时器
        self.fc = (30, 30, 30)  # 初始轨道颜色
        self.fl = 200  # 泛光最大亮度

    def update(self, dt):
        if self.b < self.t:
            self.b += dt
            self.alpha = int(self.ia + (self.fa - self.ia) * (self.b / self.t))
        else:
            self.alpha = self.fa
        self.alpha = max(0, min(255, self.alpha))

        if self.isf:
            self.ft += dt
            if self.ft >= self.fd:
                self.isf = False
                self.ft = 0
                self.fc = (30, 30, 30)  # 闪烁结束后恢复正常颜色
            else:
                if self.ft < self.fd / 2:
                    bt = int(self.fl * (self.ft / (self.fd / 2)))
                else:
                    bt = int(self.fl * (1 - ((self.ft - self.fd / 2) / (self.fd / 2))))
                self.fc = (bt, bt, bt)

        for note in self.notes:
            note.update(dt)
            if isinstance(note, Hold):
                key_mapping = {0: pygame.K_s, 1: pygame.K_d, 2: pygame.K_j, 3: pygame.K_k}
                key = key_mapping[self.id]
                key_down = pygame.key.get_pressed()[key]
                note.update_hold(key_down)

    def draw(self):
        s = pygame.Surface((self.track.width, self.track.height), pygame.SRCALPHA)
        s.fill((*self.fc, self.alpha))
        screen.blit(s, self.track.topleft)
        pygame.draw.rect(screen, (255, 255, 255, self.alpha), self.track, 1)
        pygame.draw.line(
            screen,
            (255, 255, 255, self.alpha),
            (self.track.left, HEIGHT - line_h),
            (self.track.right, HEIGHT - line_h)
        )
        for note in self.notes:
            note.draw()

    def start_flash(self):
        self.isf = True
        self.ft = 0

        

# 音符按键类
class Note:
    def __init__(self, idx, note_type, at, mt):
        self.scored = False
        self.id = idx
        self.Num = None
        self.image = load_image(type_dict.get(note_type, 'tap'))
        self.rect = self.image.get_rect()
        self.at = at
        self.mt = mt
        self.dt = 0
        self.wt = 0
        self.type = 'Tap'
        self.status = None
        self.alive = True
        self.box = pygame.Rect(setx(idx), 0, track_w, 20)
        self.box.bottom = 0
        self.sy = self.box.y + self.box.height // 2  # 碰撞箱中心线
        self.ty = HEIGHT - line_h  # 碰撞箱的中心线来判定
        self.td = self.ty - self.sy
        self.active = False
    
    def update(self, dt):
        if self.wt < self.at:
            self.wt += dt
            self.active = False
            return
        self.active = True
        self.dt += dt
        pre = self.dt / self.mt
        self.box.y = self.sy + self.td * pre
        self.rect.center = self.box.center
        self.auto_judge()
    def draw(self):
        if self.active:
            screen.blit(self.image, self.rect)

    def auto_judge(self):
        ofs = (self.dt - self.mt) * 1000
        if ofs < -80:
            return None
        if ofs > 80 and self.status == None:
            self.status = 'miss'
            print(f"轨道{self.id} 判定结果: {self.status} 时间{self.at} 第{self.Num}个 (偏移: {ofs:.3f}ms)")
            self.alive = False
            return self.status

    def judge(self):
        if not self.active or self.status is not None:
            return
        ofs = (self.dt - self.mt) * 1000
        if ofs < -80:
            return
        if -50 <= ofs <= 50:
            self.status = 'perfect'
        elif -80 <= ofs <= 80:
            self.status = 'good'
        if self.status is not None:
            self.alive = False
            print(f"轨道{self.id} 判定结果: {self.status} 时间{self.at} 第{self.Num}个 (偏移: {ofs:.3f}ms)")
        return self.status

# 长按音符类
class Hold(Note):
    def __init__(self, idx, note_type, at, mt, hd):
        super().__init__(idx, note_type, at, mt)
        self.completed = False 
        self.hd = hd  # 长按持续时间
        self.ha = False  # 是否处于长按状态
        self.hp = 0  # 长按进度 (0.0 - 1.0)
        self.type ='Hold'
        self.hr = None  # 长按矩形
        self.ht = 0  # 长按开始时间
        self.th = 0  # 长按矩形初始高度
        self.holding = False  # 是否已进入长按状态
        self.bv = True  # 身体矩形是否可见
        self.ch()

    def ch(self):
        speed = self.td / self.mt
        self.th = self.hd * speed

    def update(self, dt):
        super().update(dt)
        if not self.holding and self.active:
            sy = self.box.top - self.th
            self.hr = pygame.Rect(
                setx(self.id),
                sy,
                track_w,
                self.th
            )
        elif self.holding:
            rt = max(0, self.hd - (self.dt - self.ht))
            self.hp = 1.0 - (rt / self.hd)
            nh = self.th * (1 - self.hp)
            self.hr = pygame.Rect(
                setx(self.id),
                (HEIGHT - line_h) - nh,
                track_w,
                nh
            )
            if self.hp >= 1.0:
                self.completed = True

    def draw(self):
        if not self.holding and self.active:
            screen.blit(self.image, self.rect)
        if self.hr and self.bv and self.hr.height > 0:
            hold_surface = pygame.Surface((self.hr.width, self.hr.height), pygame.SRCALPHA)
            if self.holding:
                color = (0, 200, 255, 180)
            else:
                color = (100, 100, 255, 150)
            pygame.draw.rect(hold_surface, color, (0, 0, self.hr.width, self.hr.height))
            if self.holding:
                ph = self.hr.height * self.hp
                pc = (255, 255, 0, 200)  # 黄色进度条
                pygame.draw.rect(
                    hold_surface,
                    pc,
                    (0, self.hr.height - ph, self.hr.width, ph)
                )
            screen.blit(hold_surface, (self.hr.x, self.hr.y))

    def judge(self):
        if not self.active or self.status is not None:
            return None
        ofs = (self.dt - self.mt) * 1000
        if ofs > 80:
            self.status = 'miss'
            self.alive = False
            return 'miss'
        if -50<=ofs <=50:
            self.holding = True
            self.ht = self.dt
            self.status = 'perfect'
            self.active = False
            self.hr = pygame.Rect(
                setx(self.id),
                (HEIGHT - line_h) - self.th,
                track_w,
                self.th
            )
            return 'perfect'
        if -80 <= ofs <= 80:
            self.holding = True
            self.ht = self.dt
            self.status = 'good'
            self.active = False
            self.hr = pygame.Rect(
                setx(self.id),
                (HEIGHT - line_h) - self.th,
                track_w,
                self.th
            )
            return 'good'

    def update_hold(self, key_down):
        if self.holding:
            if not key_down:
                self.alive = False
                return 'miss'
            return self.status
        return None

    def auto_judge(self):
        if not self.active:
            return
        ofs = (self.dt - self.mt) * 1000
        if ofs > 80 and self.status is None:
            self.status = 'miss'
            self.alive = False
            return 'miss'
        if self.holding == True and self.dt > self.ht + self.hd:
            self.alive = False

# 新手教程场景
class Guide(Scene):
    def __init__(self, image, on, width=None, height=None):
        super().__init__(image, on, width, height)
        self.actors.append(Item('return', 0, 100))
        self.pops.append(APop(640, 320, 'kuang', '欢迎来到AOI!', 'fonts/pix2.ttf', 64))
        self.pops.append(APop(640, 320, 'kuang', '感受旋律和节拍,敲击音符吧!', 'fonts/pix2.ttf', 64))
        self.pops.append(APop(640, 320, 'kuang', '四个轨道从左往右对应键盘的SDJK\n按下对应的按键时,轨道会闪烁', 'fonts/pix2.ttf', 18))
        self.pops.append(APop(640, 320, 'kuang', '这是Tap音符,当其与下方判定线重合时\n敲击对应的轨道', 'fonts/pix2.ttf', 18))
        self.pops.append(APop(640, 320, 'kuang', '这是Hold音符\n当其头部的Tap与下方判定线重合时\n长按对应的轨道,直到消失', 'fonts/pix2.ttf', 18))
        self.pops.append(APop(640, 320, 'kuang', '教程结束,点击返回菜单界面', 'fonts/pix2.ttf', 64))
        self.index = 0
        self.st = 0
        self.et = 2
        self.font_flag = 0
        self.Hold_add = False
        self.Tracks = [Track(i) for i in range(0, 4)]
        self.tap_add = False
        self.set(640, 360, 0)
        self.set(640, 360, 1)
        self.set(160, 360, 2)
        self.set(160, 360, 3)
        self.set(160, 360, 4)
        self.set(640, 360, 5)

    def set(self, x, y, idx):
        self.pops[idx].rect.center = (x, y)

    def update(self, dt):
        self.bob.update(dt)
        for i in self.actors:
            i.update()
        self.st += dt
        if self.st >= self.et:
            self.st = 0
            if self.index != 2 and self.font_flag < 5:
                self.font_flag += 1
            self.index += 1
        if self.font_flag < len(self.pops):
            self.pops[self.font_flag].update(dt)
        if self.index >= 2:
            if self.font_flag == 3 and not self.tap_add:
                new_note = Note(0, 0, 0, 1)
                self.Tracks[0].notes.append(new_note)
                self.tap_add = True
                print("Tap音符已生成")
            if self.font_flag == 4 and not self.Hold_add:
                new_hold = Hold(0, 0, 0, 1, 1)
                self.Tracks[0].notes.append(new_hold)
                self.Hold_add = True
                print("Hold音符已生成")
            for track in self.Tracks:
                track.update(dt)
        for i in self.Tracks:
            for note in i.notes:
                if note.type == 'Hold':
                    if note.completed == True:
                        note.alive = 0
                if not note.alive:
                    i.notes.remove(note)

    def draw(self):
        screen.fill((0, 0, 0))
        screen.blit(self.back, self.rect)
        self.bob.draw()
        if self.Hold_add and not self.Tracks[0].notes:
            self.pops[5].draw()
            return
        for i in self.actors:
            i.draw()
        for i in range(0, self.font_flag + 1):
            if i == self.font_flag:
                self.pops[i].draw()
        if self.index >= 2:
            for track in self.Tracks:
                track.draw()

    def reset(self):
        self.index = 0
        self.st = 0
        self.et = 2
        self.font_flag = 0
        self.Hold_add = False
        for i in self.pops:
            i.reset()
        self.Tracks = [Track(i) for i in range(0, 4)]
        self.tap_add = False

    def on_key_down(self, key):
        key_mapping = {
            pygame.K_s: 0,
            pygame.K_d: 1,
            pygame.K_j: 2,
            pygame.K_k: 3
        }
        if key in key_mapping:
            track_id = key_mapping[key]
            self.Tracks[track_id].start_flash()
            for note in list(self.Tracks[track_id].notes):
                if note.status is None:
                    result = note.judge()
                    if result:
                        print(f"轨道{track_id} 判定结果: {result}")
                

# 菜单场景
class menu(Scene):
    def __init__(self, image, on, width=None, height=None):
        super().__init__(image, on, width, height)
        self.actors.append(Item('kbn', 0, 650))
        self.pops.extend([pop(720, 90, 'kuang', '曲目选择', 'fonts/pix2.ttf', 64),
                          pop(720, 270, 'kuang', '新手教程', 'fonts/pix2.ttf', 64),
                          pop(720, 450, 'kuang', '退出游戏', 'fonts/pix2.ttf', 64)])

    def update(self, dt):
        return super().update(dt)

# 选曲场景
class songs(Scene):
    def __init__(self, image, on, width=None, height=None):
        super().__init__(image, on, width, height)
        self.actors.append(Item('return', 0, 100))
        self.pops.append(pop(0, 120, 'wbk', 'BRAVE:ROAD', 'fonts/pix2.ttf', 32))
        self.pops.append(pop(0, 280, 'wbk', 'GALACTIC WARZONE', 'fonts/pix2.ttf', 32))
        self.song_pic = []
        self.song_pic.append(Item('BRAVE', 640, 480, 640, 480))
        self.song_pic.append(Item('hoze', 640, 480, 640, 480))
        self.idx = -1
        # 添加开始按钮的属性
        self.flag = False
        self.bs = 144  # 按钮大小
        self.bc = BLUE  # 默认颜色
        self.hc = LIGHT_BLUE  # 鼠标悬停时的颜色
        self.bx = WIDTH - self.bs - 20  # 按钮 x 坐标
        self.by = HEIGHT - self.bs - 20  # 按钮 y 坐标
        self.ih = False  # 标记鼠标是否悬停在按钮上

    def reset(self):
        self.idx = -1
        pygame.mixer.music.load("music/start.mp3")
        pygame.mixer.music.play(-1)
        self.flag = False  # 重置时隐藏按钮
        self.ih = False  # 重置鼠标悬停状态

    def upd(self, pos):
        for id, it in enumerate(self.pops):
            if it.rect.collidepoint(pos):
                print(id)
                self.idx = id
                pygame.mixer.music.load(musics[id])
                pygame.mixer.music.play(-1)
                self.flag = True  # 点中曲目时显示按钮

        # 检查是否点击了开始按钮
        if self.flag:
            if (self.bx <= pos[0] <= self.bx + self.bs and
                    self.by <= pos[1] <= self.by + self.bs):
                print("开始游戏，加载谱面")
                return True
        return False

    def update(self, dt):
        if self.flag:
            # 获取鼠标位置
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # 检查鼠标是否悬停在按钮上
            if (self.bx <= mouse_x <= self.bx + self.bs and
                    self.by <= mouse_y <= self.by + self.bs):
                self.ih = True
            else:
                self.ih = False
        return super().update(dt)

    def draw(self):
        super().draw()
        for id, it in enumerate(self.song_pic):
            if id == self.idx:
                it.draw()
        # 绘制开始按钮
        if self.flag:
            bc = self.hc if self.ih else self.bc
            tp = [
                (self.bx, self.by),
                (self.bx + self.bs, self.by + self.bs // 2),
                (self.bx, self.by + self.bs)
            ]
            pygame.draw.polygon(screen, bc, tp)
            pygame.draw.polygon(screen, BLACK, tp, 2)

# 游戏场景
class play(Scene):
    def __init__(self, image, on, width=None, height=None):
        super().__init__(image, on, width, height)
        self.Tracks = [Track(i) for i in range(0, 4)]
        self.ms = False #音乐是否开始
        self.mt = 0 #音乐是否结束
        self.loaded = False
        self.combo = 0
        self.score = 0
        self.chart = None
        self.ahold = {} #头判成功判定，仍处于长按的hold
        self.ps = 0
        self.gs = 0
        self.mss = 0
        self.cb = 0
        self.paused = False  # 暂停状态
        # 暂停按钮
        self.pause_button = pop(WIDTH-50, 20, 'kuang', "PAUSE", 'fonts/pix2.ttf', 32, False)
        # 暂停菜单按钮
        self.pause_menu = [
            pop(WIDTH//2, HEIGHT//2 - 100, 'wbk', "继续", 'fonts/pix2.ttf', 48),
            pop(WIDTH//2, HEIGHT//2, 'wbk', "重开", 'fonts/pix2.ttf', 48),
            pop(WIDTH//2, HEIGHT//2 + 100, 'wbk', "返回选曲", 'fonts/pix2.ttf', 48)
        ]
        self.fout = False
        self.fa = 255
        self.fd = 2.0  # 2秒淡出时间
        self.ft = 0.0
        self.me = False
        # 设置按钮位置
        for btn in self.pause_menu:
            btn.rect.center = (WIDTH//2, btn.rect.centery)
        self.pause_button.rect.topright = (WIDTH-10, 10)
        self.jr = None  # 存储当前的判定结果
        self.jt = 0      # 显示计时器
        self.jd = 0.2 # 显示持续时间（秒）
        self.jp = (WIDTH//2, HEIGHT//3)  # 显示位置

    def load_chart(self, chart_data):  # 加载谱面
        if not self.loaded:
            tol = 0
            for note_data in chart_data["notes"]:
                track = note_data["track"]
                time = note_data["time"] - 0.5
                note_type = note_data["type"]
                tol += 1
                if note_type == "tap":
                    new_note = Note(track, 0, time, 0.625)  
                    new_note.Num = tol
                elif note_type == "hold":
                    duration = note_data.get("duration", 1.0)
                    new_note = Hold(track, 0, time, 0.625, duration)
                    new_note.Num = tol
                self.Tracks[track].notes.append(new_note)
            self.loaded = True

    def update(self, dt):
        if self.fout:
            self.ft += dt
            # 计算透明度 (0-255)
            self.fa = max(0, int(255 * (1 - self.ft / self.fd)))
            
            # 淡出完成后切换到结算场景
            if self.ft >= self.fd:
                return "game_over"
            return
        
        # 如果暂停，不更新游戏状态
        if self.paused:
            return
            
        # 检测音乐是否播放结束来判断是否游玩结束
        if self.ms and not pygame.mixer.music.get_busy() and not self.me:
            self.me = True
            self.over()


        ok = all([track.alpha == 255 for track in self.Tracks]) #轨道渐入完毕后，开始播放音乐与note更新
        if ok and not self.ms:
            pygame.mixer.music.play()
            self.ms = True
            self.mt = pygame.time.get_ticks() / 1000.0

        # 获取当前按键状态（用于长按检测）
        key_state = {
            0: pygame.key.get_pressed()[pygame.K_s],
            1: pygame.key.get_pressed()[pygame.K_d],
            2: pygame.key.get_pressed()[pygame.K_j],
            3: pygame.key.get_pressed()[pygame.K_k]
        }
        if self.jr is not None:
            self.jt += dt
        if self.jt >= self.jd:
            self.jr = None
        # 处理所有轨道的音符
        for track_id, track in enumerate(self.Tracks):
            track.update(dt)
            
            # 处理当前轨道的音符
            for note in list(track.notes):
                # 处理未判定的音符（包括Tap和Hold头部）
                if note.status is None and note.active:
                    note.auto_judge()
                if note.status is not None and not getattr(note, 'scored', False):

                    # print(f"第{note.Num}个,类型{note.type},判分") 调试用
                    note.scored = True
                    
                    if note.status != 'miss':
                        self.combo += 1
                        hit_e.play()
                        self.jr = note.status.upper()  # 转换为大写
                        self.jt = 0  # 重置计时器
                        self.cb = max(self.cb,self.combo)
                        self.score += scs[note.status]
                        if note.status == 'perfect':
                            self.ps+=1
                        else:
                            self.gs+=1
                        print(f"判定成功: {note.status} 分数+{scs[note.status]}")
                    else:
                        self.combo = 0
                        self.mss+=1
                        print("MISS! 连击中断")
                    
                    # 如果是Hold头部判定成功，开始跟踪长按
                    if isinstance(note, Hold) and note.status in ['perfect', 'good']:
                        self.ahold[track_id] = note
                
                # 处理长按音符的身体部分
                if isinstance(note, Hold) and note.holding:
                    # 检查按键状态
                    if not key_state[track_id]:
                        # 松开按键，长按中断
                        note.status = 'miss'
                        self.mss+=1
                        note.alive = False
                        self.combo = 0
                        print("长按中断! MISS")
                        # 从活跃长按中移除
                        if track_id in self.ahold:
                            del self.ahold[track_id]
                    
                    # 检查长按是否完成
                    elif note.completed:
                        self.combo += 1
                        self.cb = max(self.cb,self.combo)
                        self.score += scs[note.status]  # 使用头部判定等级
                        note.alive = False
                        if note.status == 'perfect':
                            self.ps+=1
                        else:
                            self.gs+=1
                        print(f"长按完成! 分数+{scs[note.status]}")
                        # 从活跃长按中移除
                        if track_id in self.ahold:
                            del self.ahold[track_id]
                
                # 移除已死亡音符
                if not note.alive:
                    track.notes.remove(note)

    def draw(self):
        screen.blit(self.back, self.rect)
        self.bob.draw()
        for track in self.Tracks:
            track.draw()
        
        # 绘制游戏信息
        font = pygame.font.Font('fonts/pix2.ttf', 36)


        text = font.render(f"Score: {self.score}", True, (230, 230, 230))
        rect = text.get_rect()
        place(rect,0,0)
        screen.blit(text, rect)

        text = font.render(f"Combo: {self.combo}", True, (230, 230, 230))
        rect = text.get_rect()
        place(rect,0,36)
        screen.blit(text, rect)
        
        text = font.render(f"Perfects: {self.ps}", True, (230, 230, 230))
        rect = text.get_rect()
        place(rect,0,72)
        screen.blit(text, rect)


        text = font.render(f"Goods: {self.gs}", True, (230, 230, 230))
        rect = text.get_rect()
        place(rect,0,108)
        screen.blit(text, rect)

        text = font.render(f"Misses: {self.mss}", True, (230, 230, 230))
        rect = text.get_rect()
        place(rect,0,144)
        screen.blit(text, rect)
        # 绘制暂停按钮
        if self.jr is not None:
        # 根据判定结果选择颜色
            if self.jr == "PERFECT":
                color = (255, 215, 0)  # 金色
                font_size = 72
            else:  # "GOOD"
                color = (0, 255, 0)    # 绿色
                font_size = 64
        
            # 创建字体
            judge_font = pygame.font.Font('fonts/pix2.ttf', font_size)
            text_surface = judge_font.render(self.jr, True, color)
            text_rect = text_surface.get_rect(center=self.jp)
            screen.blit(text_surface, text_rect)
        self.pause_button.draw()
        
        # 如果暂停，绘制暂停菜单
        if self.paused:
            # 添加半透明遮罩
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # 半透明黑色
            screen.blit(overlay, (0,0))
            
            # 绘制暂停菜单
            for btn in self.pause_menu:
                btn.draw()
                
            # 添加中央暂停文本
            pause_text = font.render("游戏暂停", True, (255, 255, 255))
            pause_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 200))
            screen.blit(pause_text, pause_rect)
        if self.fout: #游戏结束淡出效果
            fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, 255 - self.fa))
            screen.blit(fade_surface, (0, 0))    
    def over(self): #开始淡出
        """开始淡出效果"""
        self.fout = True
        self.ft = 0.0
        self.fa = 255    


    def on_key_down(self, key):
        key_mapping = {
            pygame.K_s: 0,
            pygame.K_d: 1,
            pygame.K_j: 2,
            pygame.K_k: 3
        }
        if key == pygame.K_e:
            self.me = True
            self.over()
            pygame.mixer.music.stop()
        if key in key_mapping:
            track_id = key_mapping[key]
            self.Tracks[track_id].start_flash()
            
            # 只触发判定，计分在update中处理
            for note in list(self.Tracks[track_id].notes):
                if note.status is None and note.active:
                    note.judge()

    def upop(self, pos):
        # 更新暂停按钮悬停状态
        self.pause_button.upop(pos)
        
        # 如果暂停，更新菜单按钮悬停状态
        if self.paused:
            for btn in self.pause_menu:
                btn.upop(pos)

    # 添加鼠标点击处理
    def upd(self, pos):
        # 处理暂停按钮点击
        if self.pause_button.rect.collidepoint(pos):
            self.paused = not self.paused
            if self.paused:
                pygame.mixer.music.pause()  # 暂停音乐
            else:
                pygame.mixer.music.unpause()  # 继续音乐
            return True
            
        # 处理暂停菜单点击
        if self.paused:
            for i, btn in enumerate(self.pause_menu):
                if btn.rect.collidepoint(pos):
                    if i == 0:  # 继续
                        self.paused = False
                        pygame.mixer.music.unpause()
                    elif i == 1:  # 重开
                        self.reset_game()
                        pygame.mixer.music.play()
                    elif i == 2:  # 返回选曲
                        self.paused = False
                        pygame.mixer.music.stop()
                        return "song_select"
            return True
        return False

    # 重置游戏状态
    def reset_game(self):
        self.paused = False
        self.ms = False
        self.loaded = False
        self.combo = 0
        self.score = 0
        self.ahold = {}
        self.mss = 0
        self.gs = 0
        self.ps = 0
        self.jr = None  # 存储当前的判定结果
        self.jt = 0      # 显示计时器
        self.jd = 0.2 # 显示持续时间（秒）
        self.Tracks = [Track(i) for i in range(0, 4)]
        # 重新加载谱面
        with open(self.chart, 'r', encoding='utf-8') as f:
            chart_data = json.load(f)
            self.load_chart(chart_data)
        pygame.mixer.music.rewind()
        self.fout = False
        self.fa = 255
        self.ft = 0.0
        self.me = False


    def change(self, image, width=None, height=None): #不同曲目用各自曲绘模糊后的图做背景
        return super().change(image, width, height)    


class over(Scene):
    def __init__(self, image, on, ps, gs, ms, tol, cb, score, width=None, height=None):
        super().__init__(image, on, width, height)
        self.ps = ps
        self.gs = gs
        self.ms = ms
        self.tol = tol
        self.cb = cb
        self.score = score
        self.rb = pop(WIDTH//2, HEIGHT-200, 'wbk', "返回选曲", 'fonts/pix2.ttf', 48)
        self.fa = 0
        self.fd = 1.0
        self.ft = 0.0
        self.fi = True
        self.rank = None
        pygame.mixer.music.load('music/end.mp3')
        pygame.mixer.music.play(-1)

    def update(self, dt):
        # 淡入效果
        if self.fi:
            self.ft += dt
            self.fa = min(255, int(255 * (self.ft / self.fd)))
            if self.ft >= self.fd:
                self.fi = False

    def draw(self):
        super().draw()  # 绘制背景和气泡
        
        # 添加淡入效果遮罩
        if self.fi:
            fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, 255 - self.fa))
            screen.blit(fade_surface, (0, 0))
        
        # 显示结算数据
        font_l = pygame.font.Font('fonts/pix2.ttf', 48)
        font_m = pygame.font.Font('fonts/pix2.ttf', 36)
        
        # 计算准确率
        acc = 0
        if self.tol > 0:
            acc = (self.ps * 1.0 + self.gs * 0.75) / self.tol * 100
        if acc == 100:
            self.rank = 'S+'
        elif acc>=95:
            self.rank = 'S'
        elif acc >=90:
            self.rank = 'A'
        elif acc >= 85:
            self.rank = 'B'
        elif acc >= 60:
            self.rank = 'C'
        else:
            self.rank = 'Failed'
        # 在屏幕中央显示
        title = font_l.render("游戏结束", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        y_pos = 150
        texts = [
            f"分数: {self.score}",
            f"最大连击: {self.cb}",
            f"准确率: {acc:.2f}%",
            f"Perfect: {self.ps}",
            f"Good: {self.gs}",
            f"Miss: {self.ms}",
            f"评级: {self.rank }"
        ]
        
        for text in texts:
            text_surface = font_m.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (WIDTH//2 - text_surface.get_width()//2, y_pos))
            y_pos += 50
        
        # 绘制返回按钮
        self.rb.draw()

    def upop(self, pos):
        self.rb.upop(pos)

    def upd(self, pos):
        if self.rb.rect.collidepoint(pos):
            return "song_select"
        return False   
# 创建场景实例
Opening = Scene('back', False)  # 开始界面实例
Menu = menu('back2', True)  # 菜单场景
guide = Guide('back3', False)  # 新手教程场景
Song_sel = songs('songback', False, 1280, 720)  # 选曲场景
Playing = play('back3', False)  # 游戏中
Playover = None  # 结算
Scenes = {0: Opening, 1: Menu, 2: guide, 3: Song_sel, 4: Playing, 5: Playover}  # 场景字典

# 主控制器
class Game:
    def __init__(self):
        self.running = True
        self.status = 0
        self.music_playing = False
        self.st = None

    def update(self, dt):
        if self.status == 4 and Playing.paused:
            return
        result = Scenes[self.status].update(dt)
        if self.status == 4 and result == "game_over":
            # 创建结算场景
            ps = Playing.ps
            gs = Playing.gs
            ms = Playing.mss
            to = ps + gs + ms
            cb = Playing.cb
            score = Playing.score
            
            # 重置游戏场景
            Playing.reset_game()
            
            # 创建结算场景
            Playover = over(spic[self.st], False, ps, gs, ms, tol, cb, score)
            Scenes[5] = Playover
            self.status = 5
        if self.status <= 1 and not self.music_playing:
            pygame.mixer.music.load("music/start.mp3")
            pygame.mixer.music.play(-1)
            self.music_playing = True

    def draw(self):
        Scenes[self.status].draw()

    def upd(self, pos):
        if self.status == 5:
            result = Scenes[self.status].upd(pos)
            if result == "song_select":
                self.status = 3
                pygame.mixer.music.load('music/sel.mp3')
                pygame.mixer.music.play(-1)
                self.st = None

                return
        if self.status == 4:  # 游戏场景
            result = Playing.upd(pos)
            if result == "song_select":  # 返回选曲界面
                Playing.reset_game()
                pygame.mixer.music.load('music/sel.mp3')
                pygame.mixer.music.play(-1)
                self.status = 3
        if self.status == 0:
            self.status = 1  # 开始界面点击进入游戏

        elif self.status == 1:  # 菜单切换处理
            for index, pop_item in enumerate(Menu.pops):
                if pop_item.rect.collidepoint(pos):
                    if index == 0:
                        print("进入曲目选择")
                        self.status = 3
                        pygame.mixer.music.load('music/sel.mp3')
                        pygame.mixer.music.play(-1)
                    elif index == 1:
                        print("进入新手教程")
                        self.status = 2
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load('music/tutorial.mp3')
                        pygame.mixer.music.play(-1)
                        self.music_playing = False
                    elif index == 2:
                        print("退出游戏")
                        self.running = False

        elif self.status == 2:
            for index, pop_item in enumerate(Scenes[self.status].actors):
                if pop_item.rect.collidepoint(pos):
                    if index == 0:
                        print("返回上一级界面")
                        guide.reset()
                        self.status = 1
            if guide.font_flag == 5:
                guide.reset()
                self.status = 1  # 新手教程中切与结束返回

        # 曲目选择界面处理
        elif self.status == 3:  # 曲目选择界面处理
            start_game = Scenes[self.status].upd(pos)
            if start_game:
                # 加载谱面文件，这里假设谱面文件是一个JSON文件
                self.st = Scenes[self.status].idx
                with open(sfile[self.st], 'r', encoding='utf-8') as f:
                        chart_data = json.load(f)
                        Playing.chart = str(sfile[self.st])
                        Playing.load_chart(chart_data)
                        Playing.change(spic[self.st])
                        pygame.mixer.music.load(musics[self.st])
                        total_notes = sum(len(track.notes) for track in Playing.Tracks)
                        print(f"已加载 {total_notes} 个音符")
                        self.status = 4
                        print("切换到游戏场景")
            for index, pop_item in enumerate(Scenes[self.status].actors):
                if pop_item.rect.collidepoint(pos):
                    if index == 0:
                        print("返回上一级界面")
                        Scenes[self.status].reset()
                        self.status = 1
        
            
    def upop(self, pos):
        if hasattr(Scenes[self.status], 'upop'):
            Scenes[self.status].upop(pos)

    def on_key_down(self, key):
        if self.status == 4 and key == pygame.K_ESCAPE:
            Playing.paused = not Playing.paused
            if Playing.paused:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
            return
        if hasattr(Scenes[self.status], 'on_key_down'):
            Scenes[self.status].on_key_down(key)

def main():
    g = Game()
    clock = pygame.time.Clock()

    while g.running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                g.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                g.upd(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                g.upop(event.pos)
            elif event.type == pygame.KEYDOWN:
                g.on_key_down(event.key)

        g.update(dt)
        screen.fill((0, 0, 0))
        g.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()