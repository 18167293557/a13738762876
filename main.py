import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.vector import Vector
import random

# 设置窗口大小
Window.size = (800, 600)

class Player(Widget):
    velocity_y = NumericProperty(0)
    gravity = NumericProperty(0.6)
    jump_power = NumericProperty(-16)
    is_jumping = BooleanProperty(False)
    is_rolling = BooleanProperty(False)
    roll_timer = NumericProperty(0)
    roll_duration = NumericProperty(40)
    original_height = NumericProperty(60)
    roll_height = NumericProperty(30)
    ground_y = NumericProperty(500)
    x = NumericProperty(100)
    y = NumericProperty(500 - 60)
    width = NumericProperty(50)
    height = NumericProperty(60)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_y = self.y
        self.update_position()
    
    def update_position(self):
        self.pos = (self.x, self.y)
        self.size = (self.width, self.height)
    
    def jump(self):
        if not self.is_jumping and not self.is_rolling:
            self.velocity_y = self.jump_power
            self.is_jumping = True
    
    def roll(self):
        if not self.is_jumping and not self.is_rolling:
            self.is_rolling = True
            self.roll_timer = self.roll_duration
            self.height = self.roll_height
            self.y += self.original_height - self.roll_height
            self.update_position()
    
    def update(self):
        # 应用重力
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        
        # 地面碰撞检测
        if self.y >= self.ground_y - self.height:
            self.y = self.ground_y - self.height
            self.velocity_y = 0
            self.is_jumping = False
        
        # 处理翻滚
        if self.is_rolling:
            self.roll_timer -= 1
            if self.roll_timer <= 0:
                self.is_rolling = False
                self.height = self.original_height
                self.y -= self.original_height - self.roll_height
                self.update_position()
        
        self.update_position()

class Obstacle(Widget):
    def __init__(self, game_speed, **kwargs):
        super().__init__(**kwargs)
        self.width = 40
        self.height = random.choice([40, 60, 80])
        self.x = Window.size[0]
        self.y = 500 - self.height
        self.game_speed = game_speed
        self.type = random.choice(['tree', 'rock', 'bush'])
        self.update_position()
    
    def update_position(self):
        self.pos = (self.x, self.y)
        self.size = (self.width, self.height)
    
    def update(self):
        self.x -= self.game_speed
        self.update_position()
    
    def get_rect(self):
        return (self.x, self.y, self.width, self.height)

class Coin(Widget):
    def __init__(self, game_speed, jump_preference=0.5, **kwargs):
        super().__init__(**kwargs)
        self.width = 30
        self.height = 30
        self.x = Window.size[0]
        self.game_speed = game_speed
        self.collected = False
        
        # 根据玩家习惯智能生成金币位置
        if jump_preference > 0.6:
            # 喜欢跳跃的玩家，金币主要在空中
            if random.random() < 0.3:
                self.y = random.randint(400, 450)
            else:
                self.y = random.randint(200, 350)
        elif jump_preference < 0.4:
            # 不喜欢跳跃的玩家，金币主要在地面
            if random.random() < 0.7:
                self.y = random.randint(400, 450)
            else:
                self.y = random.randint(200, 350)
        else:
            # 习惯中立，金币位置随机
            self.y = random.randint(200, 450)
        
        self.update_position()
    
    def update_position(self):
        self.pos = (self.x, self.y)
        self.size = (self.width, self.height)
    
    def update(self):
        self.x -= self.game_speed
        self.update_position()
    
    def get_rect(self):
        return (self.x, self.y, self.width, self.height)

class MainScreen(Screen):
    def start_infinite_mode(self, instance):
        app = App.get_running_app()
        app.start_game('infinite')
    
    def start_level_mode(self, instance):
        app = App.get_running_app()
        app.start_game('level')

class GameScreen(Screen):
    player_pos = ListProperty([100, 440])
    score_text = StringProperty('得分: 0')
    coins_text = StringProperty('金币: 0')
    mobile_mode = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player()
        self.obstacles = []
        self.coins = []
        self.score = 0
        self.coins_collected = 0
        self.game_speed = 5
        self.game_over = False
        self.game_mode = 'infinite'
        self.level = 1
        self.level_progress = 0
        self.level_target = 1000
        self.obstacle_timer = 0
        self.coin_timer = 0
        self.game_started = False
        
        # 玩家习惯检测
        self.jump_count = 0
        self.roll_count = 0
        self.total_actions = 0
        self.jump_preference = 0.5
        self.habit_sample_count = 0
        self.h_update_timer = 0
        
        # 追逐动画
        self.chase_animation_active = False
        self.chaser_x = Window.size[0] + 200
        self.chaser_y = 440
        self.chase_dialogue_index = 0
        self.chase_animation_timer = 0
        
        # 设备检测
        self.auto_detect_device()
        
        # 绑定键盘事件
        self._keyboard = Window.request_keyboard(self._on_keyboard_down, self)
    
    def auto_detect_device(self):
        """自动检测设备类型"""
        screen_width = Window.size[0]
        screen_height = Window.size[1]
        
        # 检测方法1：屏幕宽度
        if screen_width < 1000:
            self.mobile_mode = True
            return
        
        # 检测方法2：屏幕比例
        aspect_ratio = screen_height / screen_width
        if aspect_ratio > 1.2:
            self.mobile_mode = True
            return
        
        self.mobile_mode = False
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'space' or keycode[1] == 'up':
            self.jump_action(None)
        elif keycode[1] == 'down':
            self.roll_action(None)
        return True
    
    def jump_action(self, instance):
        if self.game_started:
            self.player.jump()
            self.jump_count += 1
            self.total_actions += 1
    
    def roll_action(self, instance):
        if self.game_started:
            self.player.roll()
            self.roll_count += 1
            self.total_actions += 1
    
    def on_touch_down(self, touch):
        if self.mobile_mode and self.game_started:
            # 检测虚拟按键点击
            # 跳跃按钮（右下）
            if touch.x > Window.size[0] - 210 and touch.x < Window.size[0] - 110:
                if touch.y < 110:
                    self.jump_action(None)
                    return True
            # 翻滚按钮（右下，左侧）
            elif touch.x > Window.size[0] - 110 and touch.x < Window.size[0] - 10:
                if touch.y < 110:
                    self.roll_action(None)
                    return True
        return super().on_touch_down(touch)
    
    def start_chase_animation(self):
        """开始追逐动画"""
        self.chase_animation_active = True
        self.chaser_x = Window.size[0] + 200
        self.chase_dialogue_index = 0
        self.chase_animation_timer = 0
    
    def on_enter(self, *args):
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.start_chase_animation()
    
    def update(self, dt):
        # 更新追逐动画
        if self.chase_animation_active:
            self.chaser_x -= 8
            self.chase_dialogue_index += 1.5
            if self.chase_animation_timer > 180:
                self.chase_animation_active = False
                self.game_started = True
            self.chase_animation_timer += 1
            return
        
        if not self.game_started:
            return
        
        # 更新玩家
        self.player.update()
        self.player_pos = [self.player.x, self.player.y]
        
        # 更新障碍物
        self.obstacle_timer += 1
        if self.obstacle_timer >= random.randint(60, 120):
            self.obstacles.append(Obstacle(self.game_speed))
            self.obstacle_timer = 0
        
        # 更新金币
        self.coin_timer += 1
        if self.coin_timer >= random.randint(80, 150):
            self.coins.append(Coin(self.game_speed, self.jump_preference))
            self.coin_timer = 0
        
        # 移动障碍物
        for obstacle in self.obstacles[:]:
            obstacle.update()
            if obstacle.x < -obstacle.width:
                self.obstacles.remove(obstacle)
        
        # 移动金币
        for coin in self.coins[:]:
            coin.update()
            if coin.x < -coin.width:
                self.coins.remove(coin)
        
        # 碰撞检测 - 障碍物
        player_rect = self.player.get_rect()
        for obstacle in self.obstacles:
            if self.check_collision(player_rect, obstacle.get_rect()):
                app = App.get_running_app()
                app.game_over()
                return
        
        # 碰撞检测 - 金币
        for coin in self.coins:
            if not coin.collected and self.check_collision(player_rect, coin.get_rect()):
                coin.collected = True
                self.coins_collected += 10
                self.coins.remove(coin)
        
        # 更新分数
        self.score += 1
        self.score_text = f'得分: {self.score}'
        self.coins_text = f'金币: {self.coins_collected}'
        
        # 更新玩家习惯
        if self.total_actions >= 10:
            self.h_update_timer += 1
            if self.h_update_timer >= 60:
                self.h_update_timer = 0
                if self.total_actions > 0:
                    new_preference = self.jump_count / self.total_actions
                    weight = 0.3
                    self.jump_preference = (1 - weight) * self.jump_preference + weight * new_preference
                    self.habit_sample_count += 1
        
        # 关卡模式逻辑
        if self.game_mode == 'level':
            self.level_progress += 1
            if self.level_progress >= self.level_target:
                self.level += 1
                self.level_progress = 0
                self.level_target += 500
                self.game_speed += 0.5
        else:
            if self.score % 500 == 0:
                self.game_speed += 0.5
    
    def check_collision(self, rect1, rect2):
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        return (x1 < x2 + w2 and x1 + w1 > x2 and
                y1 < y2 + h2 and y1 + h1 > y2)

class GameOverScreen(Screen):
    final_score_text = StringProperty('最终得分: 0')
    final_coins_text = StringProperty('收集金币: 0')
    
    def __init__(self, score, coins, **kwargs):
        super().__init__(**kwargs)
        self.final_score_text = f'最终得分: {score}'
        self.final_coins_text = f'收集金币: {coins}'
    
    def restart_game(self, instance):
        app = App.get_running_app()
        app.restart()
    
    def go_to_menu(self, instance):
        app = App.get_running_app()
        app.show_menu()

class LaoNaiPaoApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(MainScreen(name='menu'))
        return self.screen_manager
    
    def start_game(self, mode):
        self.game_mode = mode
        game_screen = GameScreen(name='game')
        game_screen.game_mode = mode
        self.screen_manager.add_widget(game_screen)
        self.screen_manager.current = 'game'
    
    def game_over(self):
        game_screen = self.screen_manager.get_screen('game')
        game_over_screen = GameOverScreen(
            game_screen.score,
            game_screen.coins_collected,
            name='game_over'
        )
        self.screen_manager.add_widget(game_over_screen)
        self.screen_manager.current = 'game_over'
    
    def restart(self):
        self.screen_manager.remove_widget(self.screen_manager.get_screen('game'))
        self.screen_manager.remove_widget(self.screen_manager.get_screen('game_over'))
        self.start_game(self.game_mode)
    
    def show_menu(self):
        self.screen_manager.remove_widget(self.screen_manager.get_screen('game'))
        self.screen_manager.remove_widget(self.screen_manager.get_screen('game_over'))
        self.screen_manager.current = 'menu'

if __name__ == '__main__':
    LaoNaiPaoApp().run()