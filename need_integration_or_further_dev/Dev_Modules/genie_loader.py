class Genie_Loader():

    def find_file(self, file_name, *data_file_dirs):
        import os
        for directory in data_file_dirs:
            if os.path.isfile(f'{directory}/{file_name}'):
                return directory
        raise FileNotFoundError(f'Could not find {file_name} in {data_file_dirs}')

    def fetch_csv_data_dask(self, data_file_name, data_file_dir, scheduler='threads',
                            n_rows=None, first_or_last='first'):
        import dask.dataframe as dd
        data_file_path = f'{data_file_dir}/{data_file_name}'
        bar_data = dd.read_csv(data_file_path, parse_dates=False)

        if n_rows:
            if first_or_last == 'first':
                bar_data = dd.read_csv(data_file_path, parse_dates=True, sample=100000000).head(n_rows)
            elif first_or_last == 'last':
                bar_data = dd.read_csv(data_file_path, parse_dates=True, sample=100000000).tail(n_rows)
        else:
            bar_data = dd.read_csv(data_file_path, parse_dates=True, sample=100000000)

        # parse the datetime column
        datetime_col = bar_data.columns[0]
        bar_data[datetime_col] = dd.to_datetime(bar_data[datetime_col])
        # bar_data[datetime_col] = bar_data[datetime_col].dt.strftime(output_format)
        if not n_rows:
            # compute the dask dataframe
            bar_data = bar_data.compute(scheduler=scheduler)

        # set the datetime column as the index
        bar_data.index = bar_data[datetime_col]
        # delete the datetime column
        del bar_data[datetime_col]
        return bar_data

    def fetch_data(self, data_file_names, data_file_dirs, **kwargs):

        import vectorbtpro as vbt
        if not data_file_dirs:
            data_file_dirs = [".", "Datas", "Sample-Data"]
        if not isinstance(data_file_names, list):
            data_file_names = [data_file_names]

        data_file_paths = []
        data_array = []

        # Loop through the data file names once to make sure all the files are present
        matching_file_directory = []
        for file_name in data_file_names:
            matching_file_directory.append(self.find_file(file_name, *data_file_dirs))

        for file_name, directory in zip(data_file_names, matching_file_directory):
            __path = f'{directory}/{file_name}'
            data_file_paths.append(__path)

            try:
                data = self.fetch_csv_data_dask(data_file_name=file_name,
                                                data_file_dir=directory,
                                                scheduler=kwargs.get('scheduler', 'threads'),
                                                n_rows=kwargs.get('n_rows', None),
                                                first_or_last=kwargs.get('first_or_last', 'first'))
            except Exception as e:
                # logger.exception(f'{e = }')
                print(f'Could not load {file_name} as a timeseries thus is being loaded but not prepared')
                import dask.dataframe as dd
                data_file_path = f'{directory}/{file_name}'
                data = dd.read_csv(data_file_path, parse_dates=False).compute(
                    scheduler=kwargs.get('scheduler', 'threads'))

            # Rename columns
            rename_columns = kwargs.get('rename_columns', None)
            if rename_columns:
                data = data.rename(columns=rename_columns)

            data_array.append(data)

        datas_dict = {}
        for data_name, data_bars in zip(data_file_names, data_array):
            data_name = data_name.split('.')[0]
            datas_dict[data_name] = data_bars

        print(f'Converting data to symbols_data obj')
        return vbt.Data.from_data(datas_dict)

        # return vbt.CSVData.fetch(data_file_paths, index_col=0,
        # parse_dates=True, infer_datetime_format=True, **kwargs)

    def fetch(self, data_file_names, data_file_dirs, **kwargs):
        return self.fetch_data(data_file_names, data_file_dirs, **kwargs)

    @staticmethod
    def load_vbt_pickle(pickle_path):
        import vectorbtpro as vbt
        return vbt.Data.load(pickle_path)

    @staticmethod
    def from_pandas(data, **kwargs):
        import vectorbtpro as vbt
        return vbt.Data.from_pandas(data, **kwargs)
