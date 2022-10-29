import multiprocessing as mp
import asyncio
from ball import BallVideoStreamTrack
from displayFrame import DisplayFrame
from recognition import recognitionTask 


async def print_pos(ballPosX, ballPosY):
    while(True):
        print('[DEBUG] Process value ball position: ', ballPosX.value, ballPosY.value)
        await asyncio.sleep(0.5)


async def main(lis, ballPosX, ballPosY):
    track = BallVideoStreamTrack()
    print('[DEBUG] Generated track', track)
    print_task = print_pos(ballPosX, ballPosY)
    df = DisplayFrame(f'display task-{1}', track)
    display_task = df.show(lis)
    tasks_done = await asyncio.gather(display_task, print_task)
    return tasks_done

if __name__ == '__main__':
    mp.set_start_method('spawn')
    lis = mp.Queue(300)  # 10s of frames
    ballPosX = mp.Value('d', 0.0)
    ballPosY = mp.Value('d', 0.0)
    process_a = mp.Process(target=recognitionTask, args=(lis, ballPosX, ballPosY))
    process_a.start()
    loop = asyncio.get_event_loop()
    try:
        asyncio.run(main(lis, ballPosX, ballPosY))
        process_a.join()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
    