from tkinter import Tk, Label, Button, PhotoImage
import time
import json


def get_config(file):
    with open(file, "r") as read_file:
        config = json.load(read_file)

    return config


class ClickerGame:
    def __init__(self):
        self.miles_per_second = 0
        self.overcame_mile_count = 0
        self.last_fixed_time = time.time()
        self.root = Tk()
        self.labels = {}

        self.root.title('Clicker_Game')

        position_conf = get_config("configs/positions.json")
        label_conf = get_config("configs/label.json")
        button_conf = get_config("configs/button.json")

        for label_name in label_conf.keys():
            label = Label(master=self.root, **label_conf[label_name])
            label.place(**position_conf[label_name])
            self.labels[label_name] = label

        transport_button_conf = button_conf['transport_buttons']
        transport_position_conf = position_conf['transport_buttons']
        for transport in transport_button_conf.keys():
            button = Button(
                master=self.root,
                **transport_button_conf[transport],
                **button_conf['transport_button']
            )
            button.place(**transport_position_conf[transport])
            button.bind('<Button-1>', self.get_new_transport_buyer(transport))

        click_button = Button(master=self.root, **button_conf['click_button'])
        click_button.place(**position_conf['click_button'])
        click_button.bind('<Button-1>', self.miles_increment)

    def update_label_text(self, label_name, text):
        self.labels[label_name]['text'] = text

    def miles_increment(self, event):
        self.overcame_mile_count += 1
        self.update_label_text(
            'score_count_label',
            "You have already overcame\n {} miles"
            .format(self.overcame_mile_count)
        )

    def use_transport(self):
        self.overcame_mile_count += self.miles_per_second
        self.update_label_text(
            'score_count_label',
            "You have already overcame\n {} miles" \
            .format(self.overcame_mile_count)
        )

        transport_use_period = 100  # ms
        self.root.after(transport_use_period, self.use_transport)

    def update_upgrades_label(self):
        update_time = 5  # seconds
        if time.time() - self.last_fixed_time > update_time:
            self.update_label_text(
                'upgrade_suggestions',
                "Buy new transports to move faster!"
            )

        transport_use_period = 100 # ms
        self.root.after(transport_use_period, self.update_upgrades_label)

    def fix_time(self):
        self.last_fixed_time = time.time()

    def get_new_transport_buyer(self, transport):
        def buy_new_transport(event):
            transport_conf = get_config("configs/transport.json")

            cost = transport_conf[transport]['cost']
            miles_per_second = transport_conf[transport]['miles-per-second']

            if cost > self.overcame_mile_count:

                self.update_label_text(
                    'upgrade_suggestions',
                    'You do not have enough miles for this transport!'
                )
            else:
                self.update_label_text(
                    'upgrade_suggestions',
                    'You successfully have bought a {}!'.format(transport)
                )

                self.overcame_mile_count -= cost
                self.miles_per_second += miles_per_second
                self.update_label_text(
                    'purchases_label',
                    "Your power : \n{}\nmiles per second"
                    .format(self.miles_per_second)
                )
                self.use_transport()

            self.fix_time()
            self.update_upgrades_label()

        return buy_new_transport

    def run(self):
        background_image = PhotoImage(file='background.gif')
        self.labels['background'].configure(image=background_image)

        self.root.mainloop()


def main():
    game = ClickerGame()
    game.run()


if __name__ == '__main__':
    main()
