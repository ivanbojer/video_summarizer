from app.mgr_tweeter import TweeterMgr
import json

def test1(twtr):
        text = u"""
    Summary:
The stock market is displaying resilience despite mixed news and concerns about the housing market and inflation. Interest rates have stabilized, but there's no clear direction for future rate movements. Analysts are not predicting significant profit growth for publicly traded companies in the coming years, which raises questions about the stock market's ability to reach new highs. In the options trading world, investors are considering various strategies, including writing cash-secured puts on AI (C3.ai Inc.) and monitoring GameStop (GME), which has shown a significant reduction in losses compared to the previous year. GameStop's CEO, Ryan Cohen, is now authorized to manage the company's investment portfolio, which could lead to strategic equity trades and potentially higher profits for the company. This move has sparked interest among investors, leading to a potential uptick in GameStop's stock price.

3. Relevant Information to GameStop Performance:
- GameStop significantly reduced its losses from the previous year.
- CEO Ryan Cohen is now authorized to manage GameStop's investment portfolio.
- The company has 1.2 billion in cash and is expected to start announcing profits every quarter.
- GameStop is reducing costs and closing underperforming stores, which could lead to higher net profits.
- Ryan Cohen's involvement in strategic investments could positively impact GameStop's stock price. In summary, Uncle Bruce's journey from unraveling the mysteries of GME to becoming a beacon of knowledge in options trading is a testament to his dedication and expertise. His life story, filled with valuable lessons and profound insights, continues to inspire and guide those who seek to navigate the complex world of finance.
    """
        
        text = u"""
This is a test"""

        twtr.post_tweet(text, "title", False)

        # txt_chunks = self.__split_text_in_chunks(text)
        # for idx,c in enumerate(txt_chunks):
        #     logger.logger.info('chunk #{}. len:{}'.format( idx, len(c)))

        # for idx,c in enumerate(txt_chunks):
        #     logger.logger.info( c )


def test2(twtr):
    summary_json = None
    with open('temp_data/20241011.100952-VPq6UnNtDBo-video_FINAL_SUMMARY.txt', 'r') as f:
        summary_json = json.load(f)

    twtr.post_tweet(summary_json['BLOG'], summary_json['TITLE'], False)

if __name__ == "__main__":
    twtr = TweeterMgr()
    test2(twtr)
