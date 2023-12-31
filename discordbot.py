from cmath import log
from distutils.sysconfig import PREFIX
import discord
from dotenv import load_dotenv
import os
load_dotenv()
import random
import socket
import time
import asyncio
import mcstatus
import pymysql
from discord.ext import tasks
import datetime
import pymysql

from datetime import datetime
from discord.ext import commands
from discord.ext import tasks
from mcstatus import JavaServer
from discord import app_commands


#PREFIX = os.environ['PREFIX']
TOKEN = os.environ['TOKEN']


class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents= discord.Intents.default())
        self.synced  = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        print(f'{self.user}으로 로그인 하였습니다.')
        game =  discord.Game('Mineplanet.kr')
        
        await self.change_presence(status=discord.Status.online, activity=game)

client = aclient()
tree =  app_commands.CommandTree(client)
server = JavaServer.lookup("mineplanet.kr")

@tasks.loop(seconds=1)
async def every_write_forum():
    dt = datetime.now()
    
    # 아침 9시 5분이면 실행
    if (dt.hour + 9 == 18 or dt.hour == 22 or dt.hour ==5):
        channel = await client.fetch_channel("{}".format(1171074136479649903))
        await channel.send("<@$1172960706895810691>\n낚시 대회가 시작되었습니다.")
    # 1초 쉼
    await asyncio.sleep(1)

    if (dt.hour == 3  + 9 and dt.min == 23):
        channel = await client.fetch_channel("{}".format(1171074136479649903))
        await channel.send("<@$1172960706895810691>\ntest")
    # 1초 쉼
    await asyncio.sleep(1)
    
@tree.command(name='서버상태',description='마인플래닛의 정보를 알려줍니다.') #서버 상태 확인
async def 서버상태(interaction: discord.Interaction):
    try:                
        status = server.status()
        await interaction.response.send_message(f"서버상태\n접속자: {status.players.online} player(s)\n핑: {round(status.latency)} ms")
        
    except:
        await interaction.response.send_message("서버에 접속할 수 없습니다.")

# @tree.command(name='시간',description='디버그용임') #서버 상태 확인
# async def 시간(interaction: discord.Interaction):
#     dt = datetime.datetime.now()
#     year = dt.year
#     await interaction.response.send_message(dt,ephemeral=True)
        
@tree.command(name = '경고', description='유저에게 경고를 부여합니다.')
async def warning(interaction: discord.Interaction, 유저: discord.Member, reason: str): 
    if interaction.user.guild_permissions.administrator:
        conn = pymysql.connect(host='svc.sel5.cloudtype.app', port=30823, user='root', password='conan0531**', db='theldb', charset='utf8')
        cur = conn.cursor()
        userinfo = []
        userinfo.clear()
        sql = 'SELECT * FROM warnings WHERE user = %s'
        cur.execute(sql, 유저.id)
        result = cur.fetchall()
        for i in result:
            for j in i:
                userinfo.append(j)
        
    
    
        print(userinfo)

        if not userinfo:
            sqltemp = "INSERT INTO warnings (user, reason, totalwarn) VALUES (%s, %s, %s);"
            cur.execute(sqltemp, (str(유저.id),reason, 1))
            userinfo = [str(유저.id),reason, 0]
            conn.commit()
        else:
            sqltemp = "INSERT INTO warnings (user, reason, totalwarn) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE user=%s, reason=%s, totalwarn=%s;"
            #sql2 = "INSERT INTO warnings (user, reason, totalwarn) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE user=%s, reason=%s, totalwarn=%s;"
            cur.execute(sqltemp, (str(유저.id),userinfo[1],userinfo[2],str(유저.id),reason, userinfo[2]+1))
            conn.commit()


        embed=discord.Embed(title="경고", description="<@{}>에게 경고가 1회 부여되었습니다.".format(유저.id), color=0xFB3B3B)
        embed.add_field(name="사유: {}".format(reason), value="누적 경고: {}\n처리자: <@{}>".format(userinfo[2]+1,interaction.user.id), inline=False)
        
        await interaction.response.send_message(embed=embed,ephemeral=True)
        channel = await client.fetch_channel("{}".format(1171070937928581223))
        await channel.send(embed=embed)

        embed=discord.Embed(title="경고", description="설백에서 경고를 1회 부여받았습니다.".format(유저.id), color=0xFB3B3B)
        embed.add_field(name="사유: {}".format(reason), value="누적 경고: {}\n처리자: <@{}>".format(userinfo[2]+1,interaction.user.id), inline=False)
        user = await client.fetch_user("{}".format(유저.id))
        await user.send(embed=embed)
        conn.close()
    
    else:
        await interaction.response.send_message("권한이 없습니다.",ephemeral=True)
        

    

@tree.command(name = '경고초기화', description='유저의 경고를 초기화합니다.')
async def warning(interaction: discord.Interaction, 유저: discord.Member):
    if interaction.user.guild_permissions.administrator:
        conn = pymysql.connect(host='svc.sel5.cloudtype.app', port=30823, user='root', password='conan0531**', db='theldb', charset='utf8')
        cur = conn.cursor()
        sql = 'UPDATE warnings SET reason = "None", totalwarn = "0" WHERE user = %s'
        cur.execute(sql, str(유저.id))
        conn.commit()
        await interaction.response.send_message("<@{}>님의 경고가 초기화 되었습니다.\n처리자: <@{}>".format(유저.id,interaction.user.id),ephemeral=True)
        channel = await client.fetch_channel("{}".format(1171070937928581223))
        await channel.send("<@{}>님의 경고가 초기화 되었습니다.".format(유저.id))
        
        embed=discord.Embed(title="경고 초기화", description="설백에서의 경고가 초기화 되었습니다.\n처리자: <@{}>".format(유저.id,interaction.user.id), color=0x68FB0E)
        user = await client.fetch_user("{}".format(유저.id))
        await user.send(embed=embed)
        conn.close()
    else:
        await interaction.response.send_message("권한이 없습니다.",ephemeral=True)

@tree.command(name = '경고조회', description='다른 유저의 경고를 확인합니다.')
async def warning(interaction: discord.Interaction, 유저: discord.Member): 
    if interaction.user.guild_permissions.administrator:
        conn = pymysql.connect(host='svc.sel5.cloudtype.app', port=30823, user='root', password='conan0531**', db='theldb', charset='utf8')
        cur = conn.cursor()
        userinfo = []
        userinfo.clear()
        sql = 'SELECT * FROM warnings WHERE user = %s'
        cur.execute(sql, 유저.id)
        result = cur.fetchall()
        for i in result:
            for j in i:
                userinfo.append(j)

        if len(userinfo) == 0:
            userinfo = [str(유저.id), "None", 0]
        print(userinfo)
        embed=discord.Embed(title="경고 조회", description="<@{}>님에게 부여된 경고".format(유저.id), color=0x18fdfd)
        embed.add_field(name="최근 경고 사유: {}".format(userinfo[1]), value="누적 경고: {}".format(userinfo[2]), inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)

        conn.close()
    else:
        await interaction.response.send_message("권한이 없습니다.",ephemeral=True)

@tree.command(name = '경고차감', description='유저의 경고를 차감합니다.')
async def warning(interaction: discord.Interaction, 유저: discord.Member, 차감횟수:int): 
    if interaction.user.guild_permissions.administrator:
        conn = pymysql.connect(host='svc.sel5.cloudtype.app', port=30823, user='root', password='conan0531**', db='theldb', charset='utf8')
        cur = conn.cursor()
        userinfo = []
        userinfo.clear()
        sql = 'SELECT * FROM warnings WHERE user = %s'
        cur.execute(sql, 유저.id)
        result = cur.fetchall()
        for i in result:
            for j in i:
                userinfo.append(j)

        if len(userinfo) == 0:
            await interaction.response.send_message("해당 유저에게 부여된 경고가 없습니다.",ephemeral=True)
            print(userinfo)
        elif userinfo[2] == 0:
            await interaction.response.send_message("해당 유저에게 부여된 경고가 없습니다.",ephemeral=True)
            print(userinfo)
        
        else:
            if userinfo[2] - 차감횟수 >= 0:
                print(userinfo)
                sql = 'UPDATE warnings SET totalwarn = %s WHERE user = %s'
                cur.execute(sql, (str(userinfo[2]-차감횟수),str(유저.id)))
                conn.commit()
                embed=discord.Embed(title="경고 차감", description="<@{}>님의 경고가 {}회 차감되었습니다.".format(유저.id,차감횟수), color=0xE7FB00)
                embed.add_field(name="최근 경고 사유: {}".format(userinfo[1]), value="누적 경고: {}\n처리자: <@{}>".format(userinfo[2]-차감횟수,interaction.user.id), inline=False)
                print(차감횟수)
                await interaction.response.send_message(embed=embed,ephemeral=True)
                channel = await client.fetch_channel("{}".format(1171070937928581223))
                await channel.send(embed=embed)

                embed=discord.Embed(title="경고", description="설백에서 경고가 {}회 차감되었습니다.".format(차감횟수), color=0xE7FB00)
                print(차감횟수)
                embed.add_field(name="최근 경고 사유: {}".format(userinfo[1]), value="누적 경고: {}\n처리자: <@{}>".format(userinfo[2]-차감횟수,interaction.user.id), inline=False)
                user = await client.fetch_user("{}".format(유저.id))
                await user.send(embed=embed)

            else:
                await interaction.response.send_message("현재 유저에게 부여된 경고 보다 차감하려 하는 경고의 수가 더 큽니다.",ephemeral=True)
            conn.close()
    else:
        await interaction.response.send_message("권한이 없습니다.",ephemeral=True)

@tree.command(name = '경고확인', description='자신의 경고를 확인합니다.')
async def warning(interaction: discord.Interaction):
    conn = pymysql.connect(host='svc.sel5.cloudtype.app', port=30823, user='root', password='conan0531**', db='theldb', charset='utf8')
    cur = conn.cursor()
    userinfo = []
    userinfo.clear()
    sql = 'SELECT * FROM warnings WHERE user = %s'
    cur.execute(sql, interaction.user.id)
    result = cur.fetchall()
    for i in result:
        for j in i:
            userinfo.append(j)

    if len(userinfo) == 0:
        userinfo = [str(interaction.user.id), "None", 0]
    print(userinfo)
    embed=discord.Embed(title="경고 조회", description="<@{}>님에게 부여된 경고".format(interaction.user.id), color=0x18fdfd)
    embed.add_field(name="최근 경고 사유: {}".format(userinfo[1]), value="누적 경고: {}".format(userinfo[2]), inline=False)
    await interaction.response.send_message(embed=embed,ephemeral=True)
    conn.close()
@tree.command(name = "추방", description = "유저를 추방합니다.")
async def warning(interaction: discord.Interaction, 유저: discord.Member, 사유: str):
    if interaction.user.guild_permissions.administrator:
        await interaction.guild.kick(유저, reason=사유)
        await interaction.response.send_message("<@{}>님이 서버에서 추방되었습니다.\n사유:{}".format(유저.id, 사유),ephemeral=True)
        
        embed=discord.Embed(title="추방", description="당신은 설백에서 추방되었습니다.".format(유저.id), color=0xFB3B3B)
        embed.add_field(name="사유: {}".format(사유), inline=False)
        user = await client.fetch_user("{}".format(유저.id))
        await user.send(embed=embed)
    else:
        await interaction.response.send_message("권한이 없습니다.",ephemeral=True)
    
@tree.command(name = "차단", description = "유저를 차단합니다.")
async def warning(interaction: discord.Interaction, 유저: discord.Member, 사유: str):
    if interaction.user.guild_permissions.administrator:
        await interaction.guild.ban(유저, reason=사유)
        await interaction.response.send_message("<@{}>님이 서버에서 차단되었습니다.\n사유:{}".format(유저.id, 사유),ephemeral=True)

        embed=discord.Embed(title="차단", description="당신은 설백에서 차단되었습니다.".format(유저.id), color=0xFB3B3B)
        embed.add_field(name="사유: {}".format(사유), inline=False)
        user = await client.fetch_user("{}".format(유저.id))
        await user.send(embed=embed)
    else:
        await interaction.response.send_message("권한이 없습니다.",ephemeral=True)
        
@tree.command(name='안녕',description='BOT_L과 인사해보세요!')
async def slash2(interaction: discord.Interaction):
    await interaction.response.send_message("안녕하세요!")
    

@tree.command(name='랜덤숫자',description='범위 내의 랜덤한 숫자를 출력합니다.')
async def slash2(interaction: discord.Interaction, 숫자: int, 숫자2: int):
    await interaction.response.send_message(random.randrange(숫자,숫자2+1))


    


# @tree.command(name='낚시대회',description='낚시대회에 관한 정보를 알려줍니다.') #낚대 상황
# async def 낚시대회(interaction: discord.Interaction):
#    now = datetime.now()
#    if datetime.today().weekday() % 2 == 0:
#         if now.hour+9 < 16:
#            await interaction.response.send_message("아직 낚시대회가 시작하지 않았습니다.(시작시간: 6시)")
        
#         elif now.hour+9 == 16:
#            await interaction.response.send_message("현재 낚시대회가 진행중입니다!")

#         else:
#            await interaction.response.send_message("오늘의 낚시대회는 종료되었습니다.(시작시간: 6시)")
           

#    else:
#         if now.hour+9 < 20:
#            await interaction.response.send_message("아직 낚시대회가 시작하지 않았습니다.(시작시간: 10시)")
        
#         elif now.hour+9 == 20:
#            await interaction.response.send_message("현재 낚시대회가 진행중입니다!")

#         else:
#            await interaction.response.send_message("오늘의 낚시대회는 종료되었습니다.(시작시간: 10시)")





    
@tree.command(name='패치노트',description='업데이트 정보를 확인하세요!')
async def 패치노트(interaction: discord.Interaction):
    await interaction.response.send_message("""```#####################패치노트#####################
- 관리자 명령어 권한 설정 오류 수정되었습니다.
- 가위바위보 기능 추가되었습니다.
- 데이터 베이스 연결 안정화 되었습니다.
- 경고 부여한 사람이 누구인지 확인 가능하도록 변경되었습니다.
```""",ephemeral=True)
    
@tree.command(name='changelog',description='개발자 전용 명령어입니다.')
async def changelog(interaction: discord.Interaction):
    if interaction.user.id == 766875066490683392:
        await interaction.response.send_message("""```#####################패치노트#####################
- 관리자 명령어 권한 설정 오류 수정되었습니다.
- 가위바위보 기능 추가되었습니다.
- 데이터 베이스 연결 안정화 되었습니다.
- 경고 부여한 사람이 누구인지 확인 가능하도록 변경되었습니다.
```""")
    else:
        await interaction.response.send_message("권한이 없거나 알 수 없는 오류가 발생하였습니다.",ephemeral=True)

@tree.command(name='버그제보', description= '디스코드 봇과 관련된 버그만 제보해 주세요.')
async def 문의(interaction: discord.Interaction, 내용 : str):
    embed=discord.Embed(title="버그 제보", description="", color=0x14ffd8)
    embed.add_field(name="버그 제보가 접수되었습니다.", value="", inline=False)
    embed.add_field(name="장난성, 부적적한 제보는 제재 사유가 될 수 있습니다.", value="", inline=False)
    embed.add_field(name="해당 제보 내용은 관리자에게 전달됩니다.", value="", inline=False)
    await interaction.response.send_message(embed=embed,ephemeral=True)

    users = await client.fetch_user("766875066490683392")
    await users.send("질문자 아이디: {} / 문의 내용: {}".format(interaction.user.id, 내용))


@tree.command(name='제보답변', description= '개발자 전용 명령어입니다.')
async def 문의답변(interaction: discord.Interaction, 아이디:str, 내용 : str):
    if interaction.user.id == 766875066490683392:
        user = await client.fetch_user("{}".format(아이디))
        await user.send("**제보 답변**\n{}".format(내용))
        await interaction.response.send_message(f"**답변완료**\n내용:{내용}")
        
    else:
        await interaction.response.send_message("권한이 없거나 알 수 없는 오류가 발생하였습니다.",ephemeral=True)

        
@tree.command(name='말하기', description= '관리자 전용 명령어 입니다.')
async def 문의답변(interaction: discord.Interaction ,내용 : str , 채널: discord.TextChannel):
    if interaction.user.guild_permissions.administrator:
        channel = await client.fetch_channel("{}".format(채널.id))
        await channel.send(내용.replace("$","\n"))
        await interaction.response.send_message("전송 완료",ephemeral=True)
    else:
        await interaction.response.send_message("권한이 없거나 알 수 없는 오류가 발생하였습니다.",ephemeral=True)

@tree.command(name='임베드', description= '관리자 전용 명령어 입니다.(/임베드사용법 명령어를 사용하여 자세한 사용법을 확인하세요.)')
async def 임베드(interaction: discord.Interaction ,채널: discord.TextChannel, 타이틀: str ,설명: str = "",필드: str = "None;None",바닥글: str = ""):
    if interaction.user.guild_permissions.administrator:
        embed=discord.Embed(title=타이틀.replace("$","\n"), description=설명.replace("$","\n"), color=0x14ffd8)

        fields=필드.split(';')

        for i in range(0,len(fields)-1,2):
            embed.add_field(name=fields[i].replace("$","\n"), value=fields[i+1].replace("$","\n"), inline=False)
        
        embed.set_footer(text=바닥글)


        channel = await client.fetch_channel("{}".format(채널.id))
        await channel.send(embed=embed)
        await interaction.response.send_message("전송 완료",ephemeral=True)
    else:
        await interaction.response.send_message("권한이 없거나 알 수 없는 오류가 발생하였습니다.",ephemeral=True)

@tree.command(name='임베드사용법', description= '관리자 전용 명령어 입니다.')
async def 임베드사용법(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("$: 줄 바꾸기\n필드1 제목;필드1 내용;필드2 제목;필드2 내용...",ephemeral=True)
    else:
        await interaction.response.send_message("권한이 없거나 알 수 없는 오류가 발생하였습니다.",ephemeral=True)
        
@tree.command(name='이미지', description= '관리자 전용 명령어 입니다.')
async def 이미지(interaction: discord.Interaction ,채널: discord.TextChannel, 주소: str):
    if interaction.user.guild_permissions.administrator:
        embed = discord.Embed(color=0x14ffd8)
        embed.set_image(url=주소)
        channel = await client.fetch_channel("{}".format(채널.id))
        await channel.send(embed=embed)
        await interaction.response.send_message("완료",ephemeral=True)
    else:
        await interaction.response.send_message("권한이 없거나 알 수 없는 오류가 발생하였습니다.",ephemeral=True)

@tree.command(name='가위바위보',description='Bot_L과 가위바위보를 해보세요.') #가위바위보
async def 가위바위보(interaction: discord.Interaction, 선택: str): 
    user_id = interaction.user.id
    rps_table = ['가위', '바위', '보']
    bot = random.choice(rps_table)
    result = rps_table.index(선택) - rps_table.index(bot) 
    if result == 0:
        await interaction.response.send_message(f'<@{user_id}>: {선택} , 봇: {bot}  비겼습니다.')
    elif result == 1 or result == -2:
        await interaction.response.send_message(f'<@{user_id}>: {선택} , 봇: {bot}  유저승')
    else:
        await interaction.response.send_message(f'<@{user_id}>: {선택} , 봇: {bot}  봇승')

        
try:
    client.run(TOKEN)
except discord.errors.LoginFailure as e:
    print("Improper token has been passed.")
