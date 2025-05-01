import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
from matplotlib import font_manager
import seaborn as sns
import matplotlib.cm as cm

emoji_font_path = "C:\\Windows\\Fonts\\seguiemj.ttf"
emoji_font = font_manager.FontProperties(fname=emoji_font_path)
plt.rcParams['font.family'] = emoji_font.get_name()


st.sidebar.title('Whatsapp Chat Analyzer')

# Using markdown to add a custom-sized label above the file uploader
st.sidebar.markdown("### :red[Upload your chats in .txt file format]")

# File uploader widget
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    if uploaded_file.name.endswith(".txt"):
        try:
            # Read the file as bytes and decode to UTF-8
            bytes_data = uploaded_file.getvalue()
            data = bytes_data.decode("utf-8")
            df = preprocessor.preprocess(data)
            # Do something with df (e.g., display analysis)
        except UnicodeDecodeError:
            st.error("Error decoding the file. Please make sure it's a UTF-8 encoded text file.")
            st.stop()
    else:
        st.error("Unsupported file format. Please upload a .txt file exported from WhatsApp.")
        st.stop()


    df = preprocessor.preprocess(data)

    #fetch unique users
    user_list = df['user'].unique().tolist()

    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        num_messages, words, num_media_messages, num_link_shared = helper.fetch_stats(selected_user, df)

        #Stats Area:-
        st.title('Top Statistics')
        col1, col2, col3, col4 = st.columns([1.2,1,1,1], gap="small", border = True)

        with col1:
            st.header(":blue[_Total Messages_]", divider="rainbow")
            st.title(num_messages)
        with col2:
            st.header(":red[_Total Words_]",divider="rainbow")
            st.title(words)
        with col3:
            st.header(":green[_Media Shared_]",divider="rainbow")
            st.title(num_media_messages)
        with col4:
            st.header(":orange[_Links Shared_]",divider="rainbow")
            st.title(num_link_shared)

        #TIMELINE:-
        # st.title("Timeline")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color="green")
            plt.xticks(rotation="vertical")
            st.pyplot(fig)
        with col2:
            st.header("Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color="orange")
            plt.xticks(rotation="vertical")
            st.pyplot(fig)

        #Activity Map:-
        # st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            norm = plt.Normalize(min(busy_day.values), max(busy_day.values))
            colors = cm.OrRd(norm(busy_day.values))
            ax.bar(busy_day.index, busy_day.values, color=colors)
            plt.xticks(rotation="vertical")
            st.pyplot(fig)
        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            norm = plt.Normalize(min(busy_month.values), max(busy_month.values))
            colors = cm.Blues(norm(busy_month.values))
            ax.bar(busy_month.index, busy_month.values, color=colors)
            plt.xticks(rotation="vertical")
            st.pyplot(fig)


        #Finding the busiest users in the group(Group level):-
        if selected_user == "Overall":
            st.header("Most active users")
            x, new_df = helper.most_busy_users(df)

            # STEP 4
            col1, col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots()
                norm = plt.Normalize(min(x.values), max(x.values))
                colors = cm.Greens(norm(x.values))
                ax.bar(x.index, x.values, color = colors)

                plt.xticks(rotation = "vertical")
                st.pyplot(fig)
            with col2:
                # st.dataframe(new_df)
                fig, ax = plt.subplots()

                ax.pie(new_df['percent'].head(), labels=new_df['user'].head(), autopct="%0.2f", pctdistance=0.85)

                # draw circle
                centre_circle = plt.Circle((0, 0), 0.70, fc='white')
                fig = plt.gcf()

                # Adding Circle in Pie chart
                fig.gca().add_artist(centre_circle)

                st.pyplot(fig)


        col1, col2 = st.columns(2)

        with col1:
            #WordCloud
            st.header("WordCloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig,ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

        with col2:
            #most common words

            most_common_df = helper.most_common_words(selected_user, df)

            fig, ax = plt.subplots()
            norm = plt.Normalize(min(most_common_df[1]), max(most_common_df[1]))
            colors = cm.GnBu(norm(most_common_df[1]))

            ax.barh(most_common_df[0], most_common_df[1], color = colors)
            plt.xticks(rotation="vertical")

            st.header("Most Common Words")
            st.pyplot(fig)

        #emoji analysis
        emoji_df = helper.emoji_helper(selected_user, df)
        st.header("Emoji Analysis")

        if(emoji_df.empty):
            st.subheader('No emojis found')
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)
            with col2:
                fig, ax = plt.subplots()
                ax.pie(emoji_df['count'].head(), labels=emoji_df['emoji'].head(), autopct="%0.2f", pctdistance=0.85)

                # draw circle
                centre_circle = plt.Circle((0, 0), 0.70, fc='white')
                fig = plt.gcf()

                # Adding Circle in Pie chart
                fig.gca().add_artist(centre_circle)

                st.pyplot(fig)

        #HeatMap
        st.header("User Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig_width = max(6, 0.5 * user_heatmap.shape[1])  # width scales with number of columns
        fig_height = max(4, 0.4 * user_heatmap.shape[0])  # height scales with rows
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax = sns.heatmap(user_heatmap, cmap="Blues")
        st.pyplot(fig)
