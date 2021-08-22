from flask import Blueprint, render_template, flash, redirect, url_for
from spectacles.db import session
from spectacles.forms import NewStonkForm
# noinspection PyPackageRequirements
from scrooge.models import Stonk
# noinspection PyPackageRequirements
from scrooge.tasks import fetch_symbol_quotes

bp = Blueprint('stonk', __name__)


@bp.route('/')
def index():
    form = NewStonkForm()
    stonks = session.query(Stonk).all()
    return render_template('stonks.html', stonks=stonks, form=form)


@bp.route('/new-stonk', methods=['POST'])
def new_stonk():
    form = NewStonkForm()
    if form.validate_on_submit():
        symbol = form.data['symbol']
        flash(f'New stonk symbol added: "{symbol}". It may take some time to fetch. Please refresh the page.')
        fetch_symbol_quotes.delay(symbol)
    return redirect(url_for('index'))
