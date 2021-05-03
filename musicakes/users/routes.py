import os

from flask import (
    flash,
    request,
    abort,
    jsonify,
    render_template,
    redirect,
    url_for
)

from sqlalchemy import or_
from sqlalchemy.sql import func

from werkzeug.utils import secure_filename

from dotenv import load_dotenv

from . import bp

from .forms import (
    UserForm
)

from ..models import (
    User,
    Artist,
    DeployCeleryTask,
    PurchaseCeleryTask
)

from ..session_utils import (
    get_user_data
)

from ..decorators import (
    requires_log_in
)

from ..aws_s3.s3_utils import (
    upload_file,
    delete_files
)

from dotenv import load_dotenv

from . import bp

load_dotenv()

# Environment variable for AWS S3 location

S3_LOCATION = os.getenv('S3_LOCATION', 'Does not exist')

# Environment variables for Ethereum blockchain

ETHEREUM_CHAIN_ID = os.getenv('ETHEREUM_CHAIN_ID', 'Does not exist')

###################################################

# User creation

###################################################


@bp.route('/users/create', methods=['GET'])
@requires_log_in
def create_user_form():
    form = UserForm()

    return render_template('forms/new_user.html', form=form)


@bp.route('/users/create', methods=['POST'])
@requires_log_in
def create_user_submission():
    form = UserForm(request.form)

    auth_id = session['profile']['user_id'][6:]

    try:

        if form.validate():

            new_username = form.username.data.lower()

            if User.query.filter(User.username==new_username).one_or_none():

                flash('The username has been taken. Please choose another username.')

                return redirect(url_for('create_user_form'))

            new_user = User(
                auth_id = auth_id,
                username = new_username
            )

            new_user.insert()

            flash('Your account has been successfully created.')

            return redirect(url_for('show_account'))

    except Exception as e:

        print(e)
        flash('Your account could not be created.')

        return redirect(url_for('create_user_form'))

###################################################

# View user

###################################################

@bp.route('/users/<int:user_id>', methods=['GET'])
def show_user(user_id):
    try:

        user_data = get_user_data()

        current_user = User.query.get(user_id)
        if current_user is None:
            abort(404)

        data = current_user.short_public()

        data['purchases'] = current_user.get_purchases()

        return render_template('users/show_user.html', user=data, userinfo=user_data)

    except Exception as e:
        print(e)
        abort(404)

###################################################

# View account

###################################################

@bp.route('/account', methods=['GET'])
@requires_log_in
def show_account():

    user, data = get_user_data(True)

    if data is None:

        abort(404)

    artist = Artist.query.filter(Artist.user_id==user.id).one_or_none()

    if artist:

        data['artist_name'] = artist.name

    else:

        data['artist_name'] = None

    pending_transactions = PurchaseCeleryTask.query.filter(PurchaseCeleryTask.user_id==user.id) \
                            .filter(PurchaseCeleryTask.is_confirmed==False) \
                            .filter(PurchaseCeleryTask.is_visible==True) \
                            .order_by(PurchaseCeleryTask.started_on.desc()).limit(5).all()

    transaction_history = PurchaseCeleryTask.query.filter(PurchaseCeleryTask.user_id==user.id) \
                            .filter(PurchaseCeleryTask.is_confirmed==True) \
                            .filter(PurchaseCeleryTask.is_visible==True) \
                            .order_by(PurchaseCeleryTask.started_on.desc()).limit(5).all()


    pending_deployments = DeployCeleryTask.query.filter(
                            DeployCeleryTask.user_id == user.id) \
                            .filter(DeployCeleryTask.is_confirmed == False) \
                            .filter(DeployCeleryTask.is_visible == True) \
                            .order_by(DeployCeleryTask.started_on.desc()) \
                            .limit(5).all()

    deployment_history = DeployCeleryTask.query.filter(DeployCeleryTask.user_id==user.id) \
                            .filter(DeployCeleryTask.is_confirmed==True) \
                            .filter(DeployCeleryTask.is_visible==True) \
                            .order_by(DeployCeleryTask.started_on.desc()).limit(5).all()

    return render_template(
        'users/show_account.html',
        userinfo=data,
        transaction_history = transaction_history,
        pending_transactions = pending_transactions,
        deployment_history = [deployment.short() for deployment in deployment_history],
        pending_deployments = [pending_deployment.short() for pending_deployment in pending_deployments]
    )

@bp.route('/account/purchases', methods=['GET'])
@requires_log_in
def show_purchases():

    user, data = get_user_data(True)

    if data is None:

        abort(404)

    data['purchases'] =  user.get_purchases()

    return render_template('users/show_purchases.html', userinfo=data)

@bp.route('/users/<int:user_id>/update_profile_picture', methods=['PUT'])
@requires_log_in
def edit_profile_picture(user_id):

    user, data = get_user_data(True)

    try:

        profile_picture_file_name = S3_LOCATION + user.auth_id + "/" +secure_filename(request.get_json()['file_name'])
        user.profile_picture = profile_picture_file_name
        user.update()

        return jsonify({
            'success': True,
        })

    except Exception as e:
        print(e)
        return jsonify({
            'success': False
        })

@bp.route('/pending_transactions', methods=['GET'])
def get_pending_transactions():


    """
    Retrieves a list of pending transactions when user clicks on notifications button
    """

    user, data = get_user_data(True)

    if data is None:

        abort(404)

    try:

        pending_purchases = PurchaseCeleryTask.query.filter(
                                        PurchaseCeleryTask.user_id == user.id) \
                                        .filter(PurchaseCeleryTask.is_confirmed == False) \
                                        .filter(PurchaseCeleryTask.is_visible == True) \
                                        .order_by(PurchaseCeleryTask.started_on.desc()) \
                                        .all()

        pending_deployments = DeployCeleryTask.query.filter(
                                        DeployCeleryTask.user_id == user.id) \
                                        .filter(DeployCeleryTask.is_confirmed == False) \
                                        .filter(DeployCeleryTask.is_visible == True) \
                                        .order_by(DeployCeleryTask.started_on.desc()) \
                                        .all()

        pending_purchases_formatted = [pending_purchase.short() for pending_purchase in pending_purchases]
        pending_deployments_formatted = [pending_deployment.short() for pending_deployment in pending_deployments]

        return jsonify({
            'success': True,
            'chain_id': ETHEREUM_CHAIN_ID,
            'pending_purchases': pending_purchases_formatted,
            'pending_deployments': pending_deployments_formatted
        })

    except:
        return jsonify({
            'success': False
        })

@bp.route('/transactions/<string:transaction_hash>/hide', methods=['POST'])
def hide_transaction(transaction_hash):

    """
    Hides a transaction from a user's transaction history
    """

    data = get_user_data()

    if data is None:

        abort(404)

    try:
        current_task = PurchaseCeleryTask.query.filter(PurchaseCeleryTask.transaction_hash==transaction_hash).one_or_none()

        if not current_task:
            current_task = DeployCeleryTask.query.filter(DeployCeleryTask.transaction_hash==transaction_hash).one_or_none()

        if current_task:
            current_task.is_visible=False
            current_task.update()

        return jsonify({
            'success': True
        })


    except Exception as e:
        print(e)
        return jsonify({
            'success': False
        })

@bp.route('/transactions/<string:transaction_hash>/update', methods=['POST'])
def update_transaction(transaction_hash):
    """
    Updates a pending transaction's status
    """

    user, data = get_user_data(True)

    if data is None:

        abort(404)

    from .tasks import remove_celery_task, check_purchase_transaction_confirmed

    try:

        current_task = PurchaseCeleryTask.query.filter(PurchaseCeleryTask.transaction_hash==transaction_hash).one_or_none()

        if current_task:

            purchase_description = current_task.purchase_description
            purchase_type = current_task.purchase_type
            purchase_type_id = current_task.purchase_type_id
            wallet_address = current_task.wallet_address
            transaction_hash = current_task.transaction_hash

            remove_celery_task(current_task.task_id)
            current_task.delete()

            new_task = check_purchase_transaction_confirmed.apply_async(
                        args=(current_task.transaction_hash,
                                user.id))

            purchase_celery_task = PurchaseCeleryTask(
                task_id = new_task.id,
                user_id = user.id,
                purchase_description = purchase_description,
                purchase_type = purchase_type,
                purchase_type_id = purchase_type_id,
                wallet_address=wallet_address,
                transaction_hash = transaction_hash,
                is_confirmed = False
            )

            purchase_celery_task.insert()

            return jsonify({
                'success': True
            })

        else:

            current_task = DeployCeleryTask.query.filter(DeployCeleryTask.transaction_hash==transaction_hash).one_or_none()

            if current_task:

                wallet_address = current_task.wallet_address
                transaction_hash = current_task.transaction_hash
                release_id = current_task.release_id

                remove_celery_task(current_task.task_id)
                current_task.delete()

                new_task = check_smart_contract_deployed.apply_async(
                            args=(current_task.transaction_hash,
                                    release_id))

                deploy_celery_task = DeployCeleryTask(
                    task_id = new_task.id,
                    user_id = user.id,
                    release_id = release_id,
                    wallet_address=wallet_address,
                    transaction_hash = transaction_hash,
                    is_confirmed = False
                )

                deploy_celery_task.insert()

                return jsonify({
                    'success': True
                })


    except Exception as e:
        print(e)
        return jsonify({
            'success': False
        })
