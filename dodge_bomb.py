import os
import random
import sys
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, 5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (5, 0),
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で与えられたRectが画面の中か外か判定
    引数：こうかとんRect or 爆弾Rect
    戻り値：真理値タプル（横, 縦）/ 画面内True, 画面外False
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate


def game_over(screen):
    # フォント設定
    font = pg.font.Font(None, 80)
    text = font.render("GAME OVER", True, (255, 255, 255))
    # 泣いているこうかとん画像（8.png）を読み込む
    crying_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 1.5)
    # 左右にこうかとんを表示する座標
    left_pos = (WIDTH // 4 - crying_kk_img.get_width() // 2, HEIGHT // 2 - crying_kk_img.get_height() // 2)
    right_pos = (3 * WIDTH // 4 - crying_kk_img.get_width() // 2, HEIGHT // 2 - crying_kk_img.get_height() // 2)
    # ブラックアウトのための半透明Surface
    blackout = pg.Surface((WIDTH, HEIGHT))
    blackout.fill((0, 0, 0))
    blackout.set_alpha(210)
    # 半透明の黒い四角を画面に描画（ブラックアウト）
    screen.blit(blackout, (0, 0))
    # ブラックアウト後にこうかとんとテキストを描画
    screen.blit(crying_kk_img, left_pos)
    screen.blit(crying_kk_img, right_pos)
    screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2 - 40))

    pg.display.update()  # 画面を更新

    # 3秒待機
    pg.time.wait(3000)




def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    サイズの異なる爆弾Surfaceを要素としたリストと加速度リストを返す。
    """
    bb_imgs = [pg.Surface((size, size), pg.SRCALPHA) for size in range(10, 110, 10)]
    for i, img in enumerate(bb_imgs):
        pg.draw.circle(img, (255, 0, 0), (img.get_width() // 2, img.get_height() // 2), img.get_width() // 2)
    bb_accs = [i for i in range(1, 11)]
    return bb_imgs, bb_accs


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_imgs, bb_accs = init_bb_imgs()
    bb_img = bb_imgs[0]
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +10, +10 # 爆弾速度ベクトル

    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        
        if kk_rct.colliderect(bb_rct):
            game_over(screen)  # ゲームオーバー画面を表示
            return

        screen.blit(bg_img, [0, 0]) 

        # こうかとんの移動処理
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        # 爆弾の移動処理
        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        
        # 爆弾のサイズと速度の上昇
        bb_img = bb_imgs[min(tmr // 250, 9)]  # サイズは最大で9番目まで
        bb_rct = bb_img.get_rect(center=bb_rct.center)
        vx = bb_accs[min(tmr // 250, 9)] * (1 if vx > 0 else -1)
        vy = bb_accs[min(tmr // 250, 9)] * (1 if vy > 0 else -1)

        screen.blit(bb_img, bb_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()