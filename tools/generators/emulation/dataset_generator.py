import random
from matplotlib import pyplot as plt
import mplfinance as mpf
import pandas as pd
import numpy as np


class DatasetGenerator:
    def __init__(self):
        self.sizes = {
            "small": 3,
            "medium": 9,
            "large": 24,
            "medium-small": 6,
            "medium-large": 15
        }

        self.categories = ["Alpha", "Delta", "High", "Low",
                           "Close", "Epsilon", "Open", "A", "B", "C"]

        self.nouns = ["dataset", "collection", "database", "archive", "repository",
                      "information", "sample", "record", "resource", "stock"]

        self.sweet = ["small", "large", "fast", "slow",
                      "colorful", "plain", "noisy", "shiny", "stock"]

    def generate_dataset(self, _categories=None, _size=None, n_max=1000, _sweet="small", volatility_probability=0.2):
        categories = 3
        size = 25
        sweet = _sweet

        # Check if _categories argument is provided
        if _categories is not None:
            if type(_categories) == str:
                if _categories in self.sizes:
                    categories = self.sizes[_categories]
            elif type(_categories) == int:
                categories = _categories
            else:
                return f"invalid categories {_categories}"

        # Check if _size argument is provided
        if _size is not None:
            if type(_size) == str:
                if _size in self.sizes:
                    size = self.sizes[_size]
            elif type(_size) == int:
                size = _size
            else:
                return f"invalid size {_size}"

        if sweet != "small":
            for i in self.sweet:
                if i == _sweet:
                    sweet = _sweet
        else:
            print("setting default sweet to small")

        dates = pd.date_range(start='2023-01-01', periods=size)

        # Generate the dataset based on the determined categories and size
        category_data = []
        dataset = []
        for category_idx in range(categories):
            category_label = self.categories[category_idx % len(
                self.categories)]

            if sweet == "fast":
                # Generate values with a bias towards an increasing trend
                trend = np.random.randint(5, 15)
                values = np.arange(trend, trend + size)
            elif sweet == "slow":
                # Generate values with a bias towards a decreasing trend
                trend = np.random.randint(-10, 0)
                values = np.arange(trend, trend + size)
            elif sweet == "colorful":
                # Generate values that "jump" between different levels
                values = np.random.choice(np.arange(1, n_max + 1), size=size)
            elif sweet == "plain":
                # Generate values with small random fluctuations
                trend = np.random.randint(-2, 3)
                values = np.arange(trend, trend + size)
            elif sweet == "noisy":
                # Generate values with intervals between random ranges
                values = np.random.randint(100, 500, size=size // 2).tolist()
                values += np.random.randint(100, 120,
                                            size=size - size // 2).tolist()
            elif sweet == "shiny":
                values.appent(self.shiny_generation(size, n_max))
            elif sweet == "stock":
                return self.stock_generation(size, n_max)
            else:
                # Default case: Generate random values
                values = np.random.randint(1, n_max + 1, size=size)

            category_data = {"label": category_label, "values": values}
            dataset.append(category_data)

        data = {category_data["label"]: category_data["values"]
                for category_data in dataset}
        df = pd.DataFrame(data, index=dates)

        return df

    def shiny_generation(self, size):
        # Generate values with changing intervals and contrarian numbers
                intervals = [(2, (100, 300)), (3, (0, 100)),
                             (1, (300, 100)), (4, (200, 100))]
                values = []
                for count, (low, high) in intervals:
                    sub_values = np.random.randint(
                        low, high + 1, size=count).tolist()
                    values.extend(sub_values)
                return values

    def stock_generation(self, size, n_max):
        dates = pd.date_range(start='2023-01-01', periods=size)
        seed = np.random.randint(1, size*n_max*3/100, size=len(dates))
        base_r = random.randint(1000, (size*3*n_max/100))
        np.random.seed(seed)

        base_price = base_r  # Starting price
        daily_return = np.random.normal(
            0.001, 0.02, size=len(dates))  # Daily returns

        # Initialize the OHLC values with the first candlestick's open, high, low, and close prices
        open_prices = [base_price]
        high_prices = [base_price]
        low_prices = [base_price]
        close_prices = [base_price]

        for i in range(1, len(dates)):
            n_r = random.randint(1, int(base_r/50))
            # Calculate the prices based on the previous close price and daily return
            # Open price is the previous close
            open_price = close_prices[i - 1]
            # Calculate close price based on return
            close_price = open_price * (1 + daily_return[i])
            high_price = max(open_price, close_price) + \
                np.random.uniform(0, n_r)
            low_price = min(open_price, close_price) - \
                np.random.uniform(0, n_r)

            # Append the calculated values to respective lists
            open_prices.append(open_price)
            close_prices.append(close_price)
            high_prices.append(high_price)
            low_prices.append(low_price)

        volume = np.random.randint(1000, 5000, size=len(dates))

        ohlc_data = list(zip(dates, open_prices, high_prices,
                         low_prices, close_prices, volume))
        df = pd.DataFrame(ohlc_data, columns=[
                          'date', 'open', 'high', 'low', 'close', 'volume'])
        df.set_index('date', inplace=True)
        return df


def plot_dataset(df):
    for column in df.columns:
        plt.plot(df.index, df[column], label=column)

    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title('Generated Dataset')
    plt.legend()
    plt.show()


# Example usage
if __name__ == "__main__":
    generator = DatasetGenerator()
    df = generator.generate_dataset(_size=500, _sweet="stock")
    mc = mpf.make_marketcolors(up='green', down='red', edge='black', wick='black')
    s = mpf.make_mpf_style(base_mpl_style='seaborn', marketcolors=mc)
    mpf.plot(df, type='candle', title='Stock Price', style=s, volume=True,mav=(20, 50), show_nontrading=True)
