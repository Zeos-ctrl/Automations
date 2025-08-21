from dataclasses import dataclass

@dataclass
class Car:
    color: str
    make: str
    speed: int = 0

    def accelerate(self):
        self.speed += 1
        return

    def stop(self):
        self.speed = 0
        return

def main():
    honda = Car('red','honda')
    honda.accelerate()
    print(f"Thats a fast honda: {honda.speed}")
    honda.stop()
    return

if __name__ == '__main__':
    main()
