#discord bot for PSN Hackathon
import discord
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime
import schedule
import random


TOKEN = 'YOUR TOKEN HERE'
#intents = discord.Intents.default()
#intents.members = True
client = discord.Client()
bot = commands.Bot(command_prefix = '!')
submissions = {}
cw_list = []
hw_li = []
meetings_li = [[]]
assignments = []
server = None
scheduling = False

def from_hour_min(string_t):
    curr = datetime.strptime(string_t, "%H:%M")
    now_time = datetime.now().replace(hour=curr.hour, minute=curr.minute, second=0)
    return now_time

@bot.event
async def on_message(message):
    global scheduling

    if message.author == bot.user:
        return

    ch = message.channel
    if ch.name == "teachers-lounge" and scheduling:
        con = message.content

        if con == "exit":
            meetings_li.pop()
            meetings_li.append([])

        elif len(meetings_li[-1]) == 0:
            meetings_li[-1].append(con)
            await message.channel.send("Enter Meeting Time ('exit' to abort)")

        elif len(meetings_li[-1]) == 1:
            meet_dt = from_hour_min(con)
            meetings_li[-1].append(meet_dt)
            meetings_li.append([])

            await message.channel.send("Meeting successfully created!")

            for channel in bot.get_all_channels():
                if channel.name == "announcements":
                    searched_role = discord.utils.get(message.channel.guild.roles, name='student')
                    await channel.send(f'{searched_role.mention} new meeting "{meetings_li[-2][0]}" scheduled for {meet_dt.strftime("%I:%M %p")}')

            scheduling = False

        #print(meetings_li)
    #print(message.author)
    await bot.process_commands(message)
@tasks.loop(minutes=1)
async def classwork():
    try:
        index = 0
        #print("interval", cw_list)

        for el in cw_list:
            if datetime.now() >= el[1]:
                for channel in bot.get_all_channels():
                    if channel.name == "announcements":
                        await channel.send(f"@everyone, Deadline for {el[0]} is up!")

                        #await el[2].send(f'Here are the submissions for {el[0]}')
                        #submits = ''
                        #print(assignments)
                        

                        submitted_dm = "[CLASSWORK] " + el[0] + " submissions received are as follows:\n"
                        
                        for student in submissions[el[0]]:
                            
                                submitted_dm += student[0].nick + " has submitted " + student[1] + "\n"
                        
                        await el[2].send(submitted_dm)






                        
                        cw_list.pop(index)

                        break
            index += 1

    except Exception as e:
        print(e)

classwork.start()


@tasks.loop(minutes=1)
async def homework():
    try:
        index = 0
        #print("interval hw", hw_li)

        for el in hw_li:
            sec_left = (el[1]-datetime.now()).seconds

            if not el[4] and sec_left <= 3600:
                for channel in bot.get_all_channels():
                    if channel.name == "announcements":
                        await channel.send(f"@student, Deadline for {el[0]} HW is in an hour! Submit asap!")
                        hw_li[index][4] = True
                        
            elif datetime.now() >= el[1]:
                for channel in bot.get_all_channels():
                    if channel.name == "announcements":
                        await channel.send(f"@everyone, Deadline for {el[0]} HW is up!")

                        submitted_dm = "[HOMEWORK] " + el[0] + " submissions received are as follows:\n"
                        
                        for student in submissions[el[0]]:
                            
                                submitted_dm += student[0].nick + " has submitted " + student[1] + "\n"
                        
                        await el[2].send(submitted_dm)

                        hw_li.pop(index)
                        break
            index += 1
        
    except Exception as e:
        print(e)

homework.start()





attendees = []

@bot.command()
async def quiz(message, *args):
    students = []
    channels = bot.get_all_channels()

    for channel in channels:
        if channel.name == args[0]:
            for user in channel.voice_states.keys():
                attendees.append(int(user))

    for member in server.members:
        for role in member.roles: 
            if role.name == "student":
                if member.id in attendees:
                    students.append(member)

    student = random.choice(students)
    await message.channel.send(student.mention)

@bot.command()
async def cw(message, *args):
    title, deadline = args[0], args[1]
    try:
        curr = datetime.strptime(deadline, "%H:%M")
    except ValueError:
        await message.channel.send('Please enter the time in a valid format("HH:MM")')
        return
    now_time = datetime.now().replace(hour=curr.hour, minute=curr.minute, second=0)
    #cw_list.append([])
    print(cw_list)
    await message.channel.send('Type the details of the assignment below. If there are no details, type none')
    msg = await bot.wait_for('message', timeout = 100)
    if msg.content.lower() != 'none':
        print(msg.content)
        cw_list.append([title, now_time, message.author, msg.content])
        print(cw_list)
    else:
        cw_list.append([title, now_time, message.author, ' '])
    for channel in bot.get_all_channels():
        if channel.name == "announcements":
            searched_role = discord.utils.get(message.channel.guild.roles, name='student')
            await channel.send(f'{searched_role.mention} class work assignment **{cw_list[-1][0]}** created by {cw_list[-1][2].nick} due at **{cw_list[-1][1].strftime("%I:%M %p")}** details are as follows \n{cw_list[-1][3]} ')
    print(cw_list)
    print(title, "assigned")
    assignments = cw_list + hw_li
    submissions[title] = []


# DD-MM-YYYY HH
@bot.command()
async def hw(message, *args):
    title, deadline = args[0], args[1]
    try:
        dead = datetime.strptime(deadline, '%d-%m-%Y %H')
    except ValueError:
        await message.channel.send('Please enter the time in a valid format("DD-MM-YYYY HH")')
        return
    #hw_li.append([title, dead, message.author])
    await message.channel.send('Type the details of the assignment below. If there are no details, type none')
    msg = await bot.wait_for('message', timeout = 100)
    if msg.content.lower() != 'none':
        print(msg.content)
        hw_li.append([title, dead, message.author, msg.content])
        print(cw_list)
    else:
        hw_li.append([title, dead, message.author, ' '])
    for channel in bot.get_all_channels():
        if channel.name == "announcements":
            searched_role = discord.utils.get(message.channel.guild.roles, name='student')
            await channel.send(f'{searched_role.mention} home work assignment **{hw_li[-1][0]}** created by {hw_li[-1][2].nick} due at **{hw_li[-1][1].strftime("%I:%M %p %d-%m-%Y")}** details are as follows \n {hw_li[-1][3]} ')
    hw_li.append([False])
    
    print(dead-datetime.now())
    print(hw_li)
    assignments = cw_list + hw_li
    submissions[title] = []

@bot.command()
async def sched(message):
    global scheduling

    if len(meetings_li[-1]) == 0:
        await message.send("Enter Meeting Title ('exit' to abort)")
        scheduling = True

@bot.command()
async def submit(message,*args):
    assignments = cw_list + hw_li
    for j in assignments:
        for i in j:
            i = str(i).lower()
    assignment = args[0].lower()
    #print(assignment)
    #print(assignments)
    if assignment in submissions.keys():
        for i in submissions[assignment]:
            if i[0] == message.author.nick:
                await message.channel.send('You have already submitted this assignment')
                return
        for i in assignments:
            if assignment == i[0]:
                await message.channel.send('Send submission link below (this link will go directly to your teacher so make sure they have access to it')
    else:
        await message.channel.send("This assignment either doesn't exist or the deadline has expired. Please contact your teacher for further details")
        
    msg = await bot.wait_for("message", timeout = 100)
    print(msg.content)
    submissions[assignment].append([msg.author,msg.content])
    print(submissions)
    await msg.delete()
    await message.channel.send('Link received')
    #await message.channel.send(f"Hello {msg.author}!")


@bot.event
async def on_ready():
    global server
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    '''
    for channel in bot.get_all_channels():
    
        if channel.name == 'General':
            #print(dir(channel))
            for i in channel.voice_states.keys():
                print(await bot.fetch_user(int(i)))
            print(channel.members)
    for member in bot.get_all_members():
        print(member)
    '''
    server = bot.get_guild('YOUR GUILD ID IN INT TYPE')


@bot.command()
async def attendance(message, *args):
    print('works')
    attendees = []
    att_msg = ''
    channels = bot.get_all_channels()
    print(channels)
    print(args[0])
    for channel in channels:
        if channel.name == args[0]:
            for user in channel.voice_states.keys():
                kid = await bot.fetch_user(int(user))

                attendees.append(str(kid))
                attendees.append('\n')
    att_msg = att_msg.join(attendees)
    await message.channel.send('Sent on your Direct Messages')    
    await message.author.send(f'{int(len(attendees)/2)} attendees in your call')
    await message.author.send(att_msg)

@bot.command()
async def hello(message, *args):
    await message.send("HOLA")

@bot.command()
async def due(message, work_arg):
    if work_arg == "cw":
        if len(cw_list) == 0:
            await message.send("Hooray! No pending class assignments!")
        else:
            cw_string = ""

            for work in cw_list:
                cw_string += work[0] + " due at " + work[1].strftime("%I:%M %p %d-%m-%Y") + "\n"
            await message.send(cw_string)

    elif work_arg == "hw":
        if len(hw_li) == 0:
            await message.send("Hooray! No pending homeworks!")
        else:
            hw_string = ""

            for work in hw_li:
                hw_string += work[0] +  " due at " + work[1].strftime("%I:%M %p %d-%m-%Y") + "\n"
            await message.send(hw_string)

    else:
        await message.send("Invalid argument received! Pass 'cw' or 'hw' instead...")

bot.run(TOKEN)
