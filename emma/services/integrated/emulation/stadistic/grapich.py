import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class GraphicsPackage:

    def create_graph_for_columns(self, df, column_names=None, graph_type='bar'):
        if column_names is None:
            column_names = df.columns.tolist()

        num_columns = len(column_names)
        num_rows = (num_columns + 1) // 2

        fig, axes = plt.subplots(num_rows, 2, figsize=(12, num_rows * 5))  # Adjust figsize as needed

        if num_rows == 1:
            axes = np.array([axes])  # Convert to a 2D array if only one row

        for i, column_name in enumerate(column_names):
            row = i // 2
            col = i % 2
            ax = axes[row, col]

            if column_name in df.columns:
                data = df[column_name]

                if graph_type == "bar":
                    ax.bar(data.index, data)
                    ax.set_xlabel('X-axis')
                    ax.set_ylabel('Y-axis')
                    ax.set_title(f'Bar Graph for {column_name}')
                elif graph_type == "line":
                    ax.plot(data.index, data)
                    ax.set_xlabel('X-axis')
                    ax.set_ylabel('Y-axis')
                    ax.set_title(f'Line Graph for {column_name}')
                elif graph_type == "scatter":
                    ax.scatter(data.index, data)
                    ax.set_xlabel('X-axis')
                    ax.set_ylabel('Y-axis')
                    ax.set_title(f'Scatter Graph for {column_name}')
                elif graph_type == "histogram":
                    ax.hist(data, bins=10)  # Adjust bin count as needed
                    ax.set_xlabel('Value')
                    ax.set_ylabel('Frequency')
                    ax.set_title(f'Histogram for {column_name}')
                # Add more cases for other graph types

            else:
                ax.axis('off')  # Hide axes for missing columns

        plt.tight_layout()
        plt.show()

# Example usage
if __name__ == "__main__":
    gp = GraphicsPackage()

    # Create a sample DataFrame
    data = {
        'A': np.random.randn(100),
        'B': np.random.randn(100),
        'C': np.random.randn(100)
    }
    df = pd.DataFrame(data)

    # Create graphs for all columns with default plot type
    gp.create_graph_for_columns(df, column_names=['C'])

    # Create scatter plots for specified columns

    gp.create_graph_for_columns(df, column_names=['A', 'C'], graph_type='scatter')
