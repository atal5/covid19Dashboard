import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
import seaborn as sns
sns.set_style('darkgrid')

URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
REC_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
DEAD_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'


class covid_conf_analysis():
    def __init__(self,path=URL):
        self.path = path
        self.covid_raw_ts = pd.read_csv(self.path)
        self.covid_recovered_ts = pd.read_csv(REC_URL)
        self.covid_dead_ts = pd.read_csv(DEAD_URL)

    
    def update_data(self):
        print('Getting latest dataset')
        self.covid_raw_ts = pd.read_csv(self.path)
        self.covid_recovered_ts = pd.read_csv(REC_URL)
        self.covid_dead_ts = pd.read_csv(DEAD_URL)


    def get_raw_data(self):
        self.update_data()
        return self.covid_raw_ts

    def get_raw_recovered_data(self):
        self.update_data()
        return self.covid_recovered_ts

    def get_raw_dead_data(self):
        self.update_data()
        return self.covid_dead_ts
    
    def get_ts_data_for_state(self,state='Illinois'):
        fil = self.covid_raw_ts['Province/State']==state
        return self.covid_raw_ts[fil].T[4:]
    
    def get_data_for_cntry(self,country='US'):
        fil_cntry = self.covid_raw_ts['Country/Region']==country
        return pd.DataFrame(self.covid_raw_ts[fil_cntry].T[4:].apply(lambda x: sum(x),axis='columns'))

    def get_latest_overall_total(self,df):
        self.update_data()
        return df.iloc[:,-1].sum()

    def get_overall_dead(self):
        self.update_data()
        return self.get_latest_overall_total(self.covid_dead_ts)

    def get_latest_dead(self):
        dead_data = self.get_raw_dead_data()
        df = dead_data.iloc[:,[1,-1]].groupby('Country/Region').sum()
        df.columns = ['num_dead']
        df = df.sort_values('num_dead',ascending=True)
        return df

    def get_overall_recovered(self):
        self.update_data()
        return self.get_latest_overall_total(self.covid_recovered_ts) 

    def get_overall_active(self):
        dead = self.get_overall_dead()
        recovered = self.get_overall_recovered()
        return self.get_latest_overall_total(self.covid_raw_ts) - dead - recovered
    
    def count_countries(self):
        return len(self.covid_raw_ts['Country/Region'].unique())
    
    def count_states(self):
        return len(self.covid_raw_ts['Province/State'].unique())
    
    def get_countries_with_more_than_one_row(self):
        cntry_list = []
        for index,row in self.covid_raw_ts.groupby('Country/Region')['Country/Region']:
            if row.count() >1:
                cntry_list.append(index)
        return np.array(cntry_list)
    
    def get_countries_with_states(self):
        fil = self.covid_raw_ts['Province/State'].isna()
        return self.covid_raw_ts.loc[~fil,'Country/Region'].unique()
    
    def get_country_list(self):
        return self.covid_raw_ts['Country/Region'].unique()
    
    def get_states_for_country(self,country='US'):
        fil = self.covid_raw_ts['Country/Region']==country
        return self.covid_raw_ts.loc[fil,'Province/State'].unique()
    
    def get_counties_for_usa_state(self,state='IL'):
        res = [x.strip().split(',') for x in self.get_states_for_country(country='US')]
        counties = []
        for item in res:
            if len(item) > 1 and (item[1].strip()==state):
                    #print(item[0])
                    counties.append(item[0])
        return counties

    def get_top_countries(self,top=10):
        agg_by_cntry = self.covid_raw_ts.groupby('Country/Region').sum()
        top_cntry = agg_by_cntry.iloc[:,-1].sort_values(ascending=False)[:top]
        return top_cntry.index.to_list()
    
    def plot_for_country(self,country='US',kind='bar'):
        data_ts = self.get_data_for_cntry(country)
        #fil=covid_raw_ts['Province/State']==state
        data_ts[25:].plot(kind=kind,figsize=(20,8))
        plt.title('Number of Cumulative Daily Cases in {} '.format(country))
        plt.show()
    
    def get_data_for_top_countries(self,top):
        top_cntry = self.get_top_countries(top)
        top_ts = pd.DataFrame()
        for cntry in top_cntry:
            data_ts = self.get_data_for_cntry(cntry)
            data_ts.columns = [cntry]
            top_ts = pd.concat([top_ts,data_ts],axis='columns')
        #top_ts = top_ts.ffill().iloc[:-1,:]
        return top_ts

    def get_data_for_world_total(self,exclude_china=False):
        if exclude_china:
            fil_china = self.covid_raw_ts['Country/Region']=='China'
            ts = self.covid_raw_ts[~fil_china]
        else:
            ts = self.covid_raw_ts
        world_total = ts.iloc[:,4:].sum(axis='rows')
        return world_total

    #TODO - Refactor this function
    def plot_top_countries(self,top=10,exclude_china=False,log_trans=False):
        plt.figure(figsize=(16,10))                
        if exclude_china:
            top = top+1
            top_ts = self.get_data_for_top_countries(top)
            top_ts = top_ts.drop(['China'],axis='columns')
            start = 25
            title = 'Top {} countries with covid cases (excluding China)'.format(top-1)
        else:
            start = 0
            top_ts = self.get_data_for_top_countries(top)
            title = 'Top {} countries with covid cases'.format(top)
        #top_ts[start:].plot(kind='line',figsize=(26,8))
        if log_trans:
            top_ts = top_ts.apply((lambda x: np.log10(x+1)),axis='columns')
        plt.plot(top_ts.index[start:],top_ts[start:])
        plt.xticks(rotation=90)
        plt.legend(top_ts.columns)
        x = top_ts[start:].shape[0]-1
        if not log_trans:
            for col in top_ts.columns:
                y = int(top_ts[start:].iloc[-1,:][col])
                plt.text(x=x,y=y+10,s=col)
        else:
            plt.ylabel('Logarithmic')
            title = title + ' - Logarithmic Plot'
            locs , labels = plt.yticks()
            #ytick_labels = [''+str(10**x) for x in locs]
            plt.yticks(locs,labels=['0.1','1','10','100','1000','10K','100K'])
        plt.title(title)
        #plt.show()
        return top_ts
    
    def plot_world_trend(self,exclude_china=False):
        world_total = self.get_data_for_world_total(exclude_china)
        plt.figure(figsize=(20,10))
        plt.plot(world_total.index,world_total.values)
        plt.scatter(world_total.index,world_total.values,color="red")
        plt.xticks(rotation=90)
        plt.show()

    def get_world_total(self):
        df = self.get_raw_data()
        total = df.iloc[:,-1].sum() 
        return total

    def get_three_countries_daily_rate_for_comparison(self,cntry1='US', cntry2='Italy',cntry3='India'):
        df1 = self.get_data_for_cntry(cntry1)
        df2 = self.get_data_for_cntry(cntry2)
        df3 = self.get_data_for_cntry(cntry3)
        df = pd.concat([df1,df2,df3],axis='columns')
        df_diff = df.diff().fillna(0)
        df_diff= df_diff.reset_index()
        df_diff.columns = ['date',cntry1,cntry2,cntry3]
        
        df_diff[cntry1] = df_diff[cntry1]/np.sum(df_diff[cntry1])
        df_diff[cntry2] = df_diff[cntry2]/np.sum(df_diff[cntry2])
        df_diff[cntry3] = df_diff[cntry3]/np.sum(df_diff[cntry3])
        
        df = df_diff.set_index('date').unstack().reset_index()
        df.columns = ['country','date','dailycases']
        return df
    
    def get_country_active_conf_dead_data(self):
        dead_raw_ts = self.get_raw_dead_data()
        recovered_raw_ts = self.get_raw_recovered_data()
        confirmed_raw_ts = self.get_raw_data()
        final_df = pd.DataFrame()
        df = confirmed_raw_ts.iloc[:,[1,-1]]
        df.columns = ['Country','Date']
        grouped = pd.DataFrame(df.groupby('Country').sum()['Date'])
        grouped.columns=['Confirmed']
        final_df = pd.concat([final_df,grouped],axis='columns')

        df = dead_raw_ts.iloc[:,[1,-1]]
        df.columns = ['Country','Date']
        grouped = pd.DataFrame(df.groupby('Country').sum()['Date'])
        grouped.columns=['Dead']
        final_df = pd.concat([final_df,grouped],axis='columns')

        df = recovered_raw_ts.iloc[:,[1,-1]]
        df.columns = ['Country','Date']
        grouped = pd.DataFrame(df.groupby('Country').sum()['Date'])
        grouped.columns=['Recovered']
        final_df = pd.concat([final_df,grouped],axis='columns')

        #final_df
        final_df['Active'] = final_df['Confirmed'] - final_df['Dead'] - final_df['Recovered']
        final_df['%Active'] = np.round((final_df['Active']/final_df['Confirmed'])*100 ,2)
        final_df['%Dead'] = np.round((final_df['Dead']/final_df['Confirmed'])*100 ,2)
        final_df = final_df.reset_index()
        #final_df = final_df.rename(columns={"Country/Region": "Country"})
        return final_df.sort_values(['Active'],ascending=False)

    #double every n days
    def get_series_double_every_n_days(self,n=2):
        doubled= [100]
        num=100
        for i in range(1,48):
            num = 100 * (2**((i)/n))
            doubled.append(num)
        #print(doubled)
        doubled_df = pd.DataFrame(doubled)
        col_name = 'Double every '+str(n)+' days'
        doubled_df.columns = [col_name]
        return doubled_df

    def get_dataset_for_log_trend(self,countries_list =['US','India','Pakistan','Italy','Germany','Singapore','Korea, South','Spain','United kingdom','Japan','China']):
        #countries_list = covid.get_country_list()
        doubled_df = self.get_series_double_every_n_days(1)
        doubled_df_7 = self.get_series_double_every_n_days(7)
        doubled_df_3 = self.get_series_double_every_n_days(3)
        doubled_df_2 = self.get_series_double_every_n_days(2)
        doubled_df_5 = self.get_series_double_every_n_days(5)
        df = pd.DataFrame()
        df = pd.concat([doubled_df,doubled_df_7,doubled_df_3,doubled_df_2,doubled_df_5],axis='columns')
        for country in countries_list:
            ts = self.get_data_for_cntry(country)
            ts = ts[ts.iloc[:,0]>=100].reset_index()
            #print(ts)
            col_name = country
            ts.columns = ['Date',col_name]
            df = pd.concat([df,ts],axis='columns')
        return df

if __name__ == '__main__':
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    covid = covid_conf_analysis(url)
    print('All set for analysis: Showing a sample plot for USA')
    #covid.plot_for_country('US')
    covid.plot_top_countries(exclude_china=False)