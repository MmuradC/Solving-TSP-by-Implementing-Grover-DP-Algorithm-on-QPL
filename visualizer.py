import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

class TSPVisualizer:
    """Visualization tools for TSP"""
    
    def visualize_dataset(self, data):
        """Visualize dataset overview"""
        distance_matrix = data['distance_matrix']
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=distance_matrix,
            colorscale='Viridis',
            text=distance_matrix,
            texttemplate='%{text}',
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title='Distance Matrix Heatmap',
            xaxis_title='City',
            yaxis_title='City',
            height=500
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def visualize_distance_matrix(self, distance_matrix):
        """Visualize distance matrix"""
        fig = go.Figure(data=go.Heatmap(
            z=distance_matrix,
            colorscale='RdYlGn_r',
            text=distance_matrix,
            texttemplate='%{text}',
            textfont={"size": 12}
        ))
        
        fig.update_layout(
            title='TSP Distance Matrix',
            xaxis_title='To City',
            yaxis_title='From City',
            height=500,
            width=600
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def compare_results(self, distance_matrix, results):
        """Compare algorithm results"""
        n = len(distance_matrix)
        
        # Generate city positions for visualization
        angle = np.linspace(0, 2*np.pi, n, endpoint=False)
        x = np.cos(angle)
        y = np.sin(angle)
        
        fig = go.Figure()
        
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        for idx, (name, data) in enumerate(results.items()):
            tour = data['optimal_tour']
            
            # Extract tour coordinates
            tour_x = [x[city] for city in tour]
            tour_y = [y[city] for city in tour]
            
            fig.add_trace(go.Scatter(
                x=tour_x,
                y=tour_y,
                mode='lines+markers',
                name=f"{name} (cost: {data['optimal_cost']:.2f})",
                line=dict(color=colors[idx % len(colors)], width=2),
                marker=dict(size=10)
            ))
        
        # Add city labels
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='text',
            text=[f'City {i}' for i in range(n)],
            textposition='top center',
            showlegend=False
        ))
        
        fig.update_layout(
            title='TSP Solutions Comparison',
            xaxis_title='X',
            yaxis_title='Y',
            height=600,
            hovermode='closest'
        )
        
        # Create comparison table
        df = pd.DataFrame([
            {
                'Algorithm': name,
                'Cost': f"{data['optimal_cost']:.2f}",
                'Time (s)': f"{data['execution_time']:.4f}",
                'Tour': ' → '.join(map(str, data['optimal_tour']))
            }
            for name, data in results.items()
        ])
        
        table_fig = go.Figure(data=[go.Table(
            header=dict(values=list(df.columns),
                       fill_color='paleturquoise',
                       align='left'),
            cells=dict(values=[df[col] for col in df.columns],
                      fill_color='lavender',
                      align='left'))
        ])
        
        table_fig.update_layout(title='Results Comparison Table', height=300)
        
        # Combine visualizations
        combined_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        combined_html += table_fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        return combined_html