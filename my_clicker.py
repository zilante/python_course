from tkinter import Tk, Label, Button, PhotoImage
import time
import json

with open("config.json", "r") as read_file:
    transport_shop = json.load(read_file)
with open("coordinates.json", "r") as read_file:
    coordinates = json.load(read_file)


class GameProgress:
    def __init__(self):
        self.miles_per_second = 0
        self.miles = 0
        self.last_fixed_time = time.time()
        self.root = Tk()
        self.root.title('Clicker_Game')

    def miles_increment(self, event):
        self.miles += 1
        score_count_label['text'] = "You have already overcame\n {} miles".format(self.miles)

    def transport(self):
        self.miles += self.miles_per_second
        score_count_label['text'] = "You have already overcame\n {} miles".format(self.miles)
        self.root.after(100, lambda: self.transport())


class Transport:
    level_number = 0

    def buy_new_transport(self, event, game):
        if transport_shop['upgrades'][self.level_number]['cost'] > game.miles:
            upgrade_suggestions['text'] = 'You do not have enough miles for this transport!'
            game.last_fixed_time = time.time()
            update_upgrades_label()
        else:
            upgrade_suggestions['text'] = \
                'You succesfully have bought a {}!'.format(transport_shop['upgrades'][self.level_number]['transport'])
            game.last_fixed_time = time.time()
            update_upgrades_label()
            game.miles -= transport_shop['upgrades'][self.level_number]['cost']
            game.miles_per_second += transport_shop['upgrades'][self.level_number]['miles-per-second']
            score_count_label['text'] = "You have already overcame\n{} miles".format(game.miles)
            purchases_label['text'] = "Your power : \n{}\nmiles per second".format(game.miles_per_second)
            game.transport()


class Helicopter(Transport):
    level_number = 0


class Plane(Transport):
    level_number = 1


class SimpleRocket(Transport):
    level_number = 2


class InterplanetaryRocket(Transport):
    level_number = 3


class InterstellarRocket(Transport):
    level_number = 4


class IntergalacticRocket(Transport):
    level_number = 5


def create_game():
    new_game = GameProgress()
    return new_game


game = create_game()


def update_upgrades_label():
    if time.time() - game.last_fixed_time > 5:
        upgrade_suggestions['text'] = 'Buy new transports to move faster!'
    game.root.after(100, update_upgrades_label)


def set_background_image():
    background_image = PhotoImage(file='orig.gif')
    return background_image


background = Label(master=game.root, height=2)
background.place(x=coordinates['background'][0], y=coordinates['background'][1], relwidth=1, relheight=1)

purchases_label = Label(game.root, text="Your power : \n1\n mile per second", height=7, bg="red", fg="yellow",
                        font=("Helvetica"))
purchases_label.place(x=coordinates['purchases_label'][0], y=coordinates['purchases_label'][1])

click_button = Button(text='Fly forward!', width=20, height=10, background="#555", foreground="#ccc",
                      font=("Helvetica"))
click_button.place(x=coordinates['click_button'][0], y=coordinates['click_button'][1])
click_button.bind('<Button-1>', game.miles_increment)

upgrade_suggestions = Label(game.root, text='Buy new transports to move faster!', fg="#eee", bg="#333", height=5,
                            width=41, font=('Helvetica'))
upgrade_suggestions.place(x=coordinates['upgrade_suggestions'][0], y=coordinates['upgrade_suggestions'][1])

score_count_label = Label(game.root, text="You have already overcame\n {} miles".format(game.miles), fg="white",
                          bg="black", font=('Helvetica'), height=5, width=27)
score_count_label.place(x=coordinates['score_count_label'][0], y=coordinates['score_count_label'][1])

helicopter_button = Button(text= "{}\n\nafter 20 miles".format(transport_shop['upgrades'][0]['transport']),
                           background="green", foreground="white", width=18, height=4, font=("Helvetica"))
helicopter_button.bind('<Button-1>', lambda event: Helicopter().buy_new_transport(event, game))
helicopter_button.place(x=coordinates['helicopter_button'][0], y=coordinates['helicopter_button'][1])

plane_button = Button(text= "{}\n\nafter 200 miles".format(transport_shop['upgrades'][1]['transport']),
                      background="brown", foreground="white", width=18, height=4, font=("Helvetica"))
plane_button.bind('<Button-1>', lambda event: Plane().buy_new_transport(event, game))
plane_button.place(x=coordinates['plane_button'][0], y=coordinates['plane_button'][1])

simple_rocket_button = Button(text="{}\n\nafter 10.000 miles".format(transport_shop['upgrades'][2]['transport']),
                              background="blue", foreground="white", width=18, height=4, font=("Helvetica"))
simple_rocket_button.bind('<Button-1>', lambda event: SimpleRocket().buy_new_transport(event, game))
simple_rocket_button.place(x=coordinates['simple_rocket_button'][0], y=coordinates['simple_rocket_button'][1])

interplanetary_rocket_button = Button(text=
                                      "{}\n\nafter 50.000 miles".format(transport_shop['upgrades'][3]['transport']),
                                      background="#555", foreground="white", width=18, height=4, font=("Helvetica"))
interplanetary_rocket_button.bind('<Button-1>', lambda event: InterplanetaryRocket().buy_new_transport(event, game))
interplanetary_rocket_button.place(x=coordinates['interplanetary_rocket_button'][0],
                                   y=coordinates['interplanetary_rocket_button'][1])

interstellar_rocket_button = Button(text=
                                    "{}\n\nafter 500.000 miles".format(transport_shop['upgrades'][4]['transport']),
                                    background="orange", foreground="white", width=18, height=4,
                                    font=("Helvetica"))
interstellar_rocket_button.bind('<Button-1>', lambda event: InterstellarRocket().buy_new_transport(event, game))
interstellar_rocket_button.place(x=coordinates['interstellar_rocket_button'][0],
                                 y=coordinates['interstellar_rocket_button'][1])

intergalactic_rocket_button = Button(text=
                                    "{}\n\nafter 20.000.000 miles".format(
                                        transport_shop['upgrades'][5]['transport']),
                                    background="black", foreground="white", width=18, height=4,
                                    font=("Helvetica"))
intergalactic_rocket_button.bind('<Button-1>', lambda event: IntergalacticRocket().buy_new_transport(event, game))
intergalactic_rocket_button.place(x=coordinates['intergalactic_rocket_button'][0],
                                  y=coordinates['intergalactic_rocket_button'][1])


def main():
    background_image = set_background_image()
    background.configure(image=background_image)
    game.root.mainloop()


if __name__ == '__main__':
    main()
