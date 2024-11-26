import os
import random
import sys
import pygame as pg
import math

# 画面の幅と高さを設定
WIDTH, HEIGHT = 1100, 650

# こうかとんの移動方向を設定（キー押下に応じて移動）
DELTA = {
    pg.K_UP: (0, -5),     # 上
    pg.K_DOWN: (0, 5),     # 下
    pg.K_LEFT: (-5, 0),    # 左
    pg.K_RIGHT: (5, 0),    # 右
}

# 作業ディレクトリを現在のファイルの場所に設定
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で与えられたRectが画面の中か外かを判定
    引数：こうかとんまたは爆弾のRect
    戻り値：横方向と縦方向の境界判定（True：画面内、False：画面外）
    """
    yoko, tate = True, True
    # 画面外に出た場合
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate


def game_over(screen):
    """
    ゲームオーバー画面を表示する
    """
    font = pg.font.Font(None, 80)  # フォントを設定
    text = font.render("GAME OVER", True, (255, 255, 255))  # テキストを描画
    crying_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.5)  # 泣いているこうかとん画像をロード

    # こうかとんの位置を設定
    left_pos = (WIDTH // 4 - crying_kk_img.get_width() // 2, HEIGHT // 2 - crying_kk_img.get_height() // 2)
    right_pos = (3 * WIDTH // 4 - crying_kk_img.get_width() // 2, HEIGHT // 2 - crying_kk_img.get_height() // 2)
    
    # 半透明のブラックアウト画面を作成
    blackout = pg.Surface((WIDTH, HEIGHT))
    blackout.fill((0, 0, 0))
    blackout.set_alpha(210)  # 半透明に設定

    screen.blit(blackout, (0, 0))  # ブラックアウトを画面に描画
    screen.blit(crying_kk_img, left_pos)  # 左側にこうかとんを表示
    screen.blit(crying_kk_img, right_pos)  # 右側にこうかとんを表示
    screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 - 40))  # "GAME OVER"テキストを表示

    pg.display.update()  # 画面を更新

    pg.time.wait(3000)  # 3秒間待機


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    爆弾の画像とサイズ、加速度のリストを返す
    """
    bb_imgs = [pg.Surface((size, size), pg.SRCALPHA) for size in range(10, 110, 10)]  # 10から100までのサイズの爆弾を作成
    for i, img in enumerate(bb_imgs):
        pg.draw.circle(img, (255, 0, 0), (img.get_width() // 2, img.get_height() // 2), img.get_width() // 2)  # 爆弾を赤い円に塗る
    bb_accs = [i for i in range(1, 11)]  # 1から10までの加速度のリストを作成
    return bb_imgs, bb_accs


def calc_following_velocity(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    爆弾がこうかとんを追いかけるための速度ベクトルを計算
    引数：org - こうかとんの位置Rect
          dst - 爆弾の位置Rect
    戻り値：(vx, vy) - 追従するための移動速度ベクトル
    """
    dx = dst.centerx - org.centerx  # x方向の差を計算
    dy = dst.centery - org.centery  # y方向の差を計算
    norm = math.sqrt(dx**2 + dy**2)  # 距離（ノルム）を計算
    if norm != 0:
        vx = dx / norm * 3  # 速度ベクトルのx成分（3は速度の係数）
        vy = dy / norm * 3  # 速度ベクトルのy成分
    else:
        vx, vy = 0, 0  # 追従する必要がない場合（距離が0）
    return vx, vy


def main():
    """
    ゲームのメインループ
    """
    pg.display.set_caption("逃げろ！こうかとん")  # ゲームウィンドウのタイトル設定
    screen = pg.display.set_mode((WIDTH, HEIGHT))  # 画面サイズの設定
    bg_img = pg.image.load("fig/pg_bg.jpg")  # 背景画像をロード
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)  # こうかとんの画像をロードし、サイズ調整
    kk_rct = kk_img.get_rect()  # こうかとんの矩形を取得
    kk_rct.center = 300, 200  # 初期位置を設定

    # 爆弾の画像と加速度の初期化
    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]  # 初期の爆弾の画像を設定
    bb_rct = bb_img.get_rect()  # 爆弾の矩形を取得
    bb_rct.centerx = random.randint(0, WIDTH)  # 爆弾の初期位置をランダムに設定
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +10, +10  # 爆弾の初期速度ベクトル

    clock = pg.time.Clock()  # ゲーム内のタイマー
    tmr = 0  # タイマー

    while True:
        for event in pg.event.get():  # イベント処理
            if event.type == pg.QUIT:  # ウィンドウが閉じられた場合
                return

        # こうかとんと爆弾が衝突したらゲームオーバー
        if kk_rct.colliderect(bb_rct):
            game_over(screen)  # ゲームオーバー画面を表示
            return

        # 背景を描画
        screen.blit(bg_img, [0, 0])

        # こうかとんの移動処理
        key_lst = pg.key.get_pressed()  # 押されたキーを取得
        sum_mv = [0, 0]  # 移動量を初期化
        for key, tpl in DELTA.items():  # 押されたキーに応じて移動量を変更
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]

        # 進行方向に応じてこうかとんの画像を回転または反転
        if sum_mv[0] != 0 or sum_mv[1] != 0:
            if sum_mv[0] > 0:  # 右方向に進むとき
                kk_img_rot = pg.transform.flip(kk_img, True, False)  # 画像を反転
            elif sum_mv[0] < 0:  # 左方向に進むとき
                kk_img_rot = kk_img  # 反転せずそのまま
            elif sum_mv[1] > 0:  # 下方向に進むとき
                kk_img_rot = pg.transform.rotozoom(kk_img, 90, 1)  # 画像を回転
            else:  # 上方向に進むとき
                kk_img_rot = pg.transform.rotozoom(kk_img, -90, 1)  # 画像を回転
        else:
            kk_img_rot = kk_img  # 動かないときは元の画像を使用

        # こうかとんの位置を更新
        kk_rct = kk_img_rot.get_rect(center=kk_rct.center)  # 画像の位置を更新
        kk_rct.move_ip(sum_mv)  # こうかとんの位置を移動
        if check_bound(kk_rct) != (True, True):  # 画面外に出ないようにする
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        # こうかとんを画面に描画
        screen.blit(kk_img_rot, kk_rct)

        # 爆弾の追従処理
        bb_vx, bb_vy = calc_following_velocity(bb_rct, kk_rct)  # 追従するための速度を計算
        bb_rct.move_ip(bb_vx, bb_vy)  # 爆弾を移動

        # 画面外に出ないように反転処理
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            bb_vx *= -1  # 横方向で画面外に出たら反転
        if not tate:
            bb_vy *= -1  # 縦方向で画面外に出たら反転

        # 爆弾のサイズを時間経過で変更
        bb_img = bb_imgs[min(tmr // 250, 9)]  # タイマーに応じて爆弾のサイズを増加
        bb_rct = bb_img.get_rect(center=bb_rct.center)  # 新しい爆弾の位置を設定

        # 爆弾を画面に描画
        screen.blit(bb_img, bb_rct)

        pg.display.update()  # 画面を更新
        tmr += 1  # タイマーを進める
        clock.tick(50)  # 1秒間に50回ループ


if __name__ == "__main__":
    pg.init()  # Pygameを初期化
    main()  # ゲーム開始
    pg.quit()  # Pygame終了
    sys.exit()  # プログラム終了
