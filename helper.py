import inspect
import polars as pl


def get_data(
    read_func,
    read_params: dict,
    fetch_func,
    fetch_params: dict,
    insert_func,
    force_update: bool,
    log: bool = True,
):
    if force_update:
        if log:
            print(f"Force updating")
        web_data = fetch_func(**fetch_params)
        if isinstance(insert_func, list):
            index = 0
            for insert in insert_func:
                insert(web_data[index])
                index += 1
        else:
            insert_func(web_data)
        local_data = read_func(**read_params)
        return local_data
    else:
        read_params = _filter_params_for_function(read_func, read_params)
        local_data = read_func(**read_params)
        if local_data.is_empty():
            if log:
                print(f"Fetching from the web for data: {read_params}")
            fetch_params = _filter_params_for_function(fetch_func, fetch_params)
            web_data = fetch_func(**fetch_params)
            if web_data is None:
                return pl.DataFrame()
            if isinstance(insert_func, list):
                index = 0
                for insert in insert_func:
                    insert(web_data[index])
                    index += 1
            else:
                insert_func(web_data)
            local_data = read_func(**read_params)
        return local_data


def _filter_params_for_function(func, params):
    sig = inspect.signature(func)
    allowed = {k: v for k, v in params.items() if k in sig.parameters}
    return allowed


def _determine_param_type(param: str):
    try:
        data = int(param)
        return "id"
    except ValueError:
        return "slug"
