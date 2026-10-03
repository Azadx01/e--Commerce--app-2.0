"""initial_schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-04 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), server_default='customer', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('1'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 2. Blacklisted Tokens table
    op.create_table(
        'blacklisted_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('blacklisted_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blacklisted_tokens_token'), 'blacklisted_tokens', ['token'], unique=True)

    # 3. Technician Profiles table
    op.create_table(
        'technician_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('business_name', sa.String(length=255), nullable=False),
        sa.Column('device_categories', sa.JSON(), nullable=True),
        sa.Column('skills', sa.JSON(), nullable=True),
        sa.Column('pricing_model', sa.String(length=255), nullable=True),
        sa.Column('service_area', sa.String(length=255), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('rating', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('review_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('verification_status', sa.String(length=50), server_default='unverified', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('1'), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_technician_profiles_id'), 'technician_profiles', ['id'], unique=False)

    # 4. Devices table
    op.create_table(
        'devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('brand', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('purchase_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('condition', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='active', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_devices_id'), 'devices', ['id'], unique=False)

    # 5. Device Images table
    op.create_table(
        'device_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 6. Diagnostics table
    op.create_table(
        'diagnostics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=True),
        sa.Column('reported_problem', sa.Text(), nullable=True),
        sa.Column('selected_symptoms', sa.JSON(), nullable=True),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('diagnosis_result', sa.JSON(), nullable=True),
        sa.Column('estimated_repair_cost', sa.Float(), nullable=True),
        sa.Column('estimated_resale_value', sa.Float(), nullable=True),
        sa.Column('recommended_action', sa.String(length=100), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnostics_id'), 'diagnostics', ['id'], unique=False)

    # 7. Decisions table
    op.create_table(
        'decisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=True),
        sa.Column('diagnostic_id', sa.Integer(), nullable=True),
        sa.Column('device_age_months', sa.Float(), nullable=True),
        sa.Column('device_condition', sa.String(length=50), nullable=True),
        sa.Column('estimated_repair_cost', sa.Float(), nullable=False),
        sa.Column('current_resale_value', sa.Float(), nullable=False),
        sa.Column('replacement_cost', sa.Float(), nullable=False),
        sa.Column('user_priority', sa.String(length=50), server_default='balanced', nullable=False),
        sa.Column('repair_ratio', sa.Float(), nullable=False),
        sa.Column('recommendation_matrix', sa.JSON(), nullable=True),
        sa.Column('chosen_action', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['diagnostic_id'], ['diagnostics.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decisions_id'), 'decisions', ['id'], unique=False)

    # 8. Repairs table
    op.create_table(
        'repairs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('technician_id', sa.Integer(), nullable=True),
        sa.Column('diagnostic_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='REQUESTED', nullable=False),
        sa.Column('problem_description', sa.Text(), nullable=True),
        sa.Column('quote_amount', sa.Float(), nullable=True),
        sa.Column('inspection_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['diagnostic_id'], ['diagnostics.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['technician_id'], ['technician_profiles.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_repairs_id'), 'repairs', ['id'], unique=False)

    # 9. Repair History table
    op.create_table(
        'repair_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('repair_id', sa.Integer(), nullable=False),
        sa.Column('from_status', sa.String(length=50), nullable=True),
        sa.Column('to_status', sa.String(length=50), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('actor_role', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['repair_id'], ['repairs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. Quotes table
    op.create_table(
        'quotes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('repair_id', sa.Integer(), nullable=False),
        sa.Column('technician_id', sa.Integer(), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('is_change_request', sa.Boolean(), server_default=sa.text('0'), nullable=False),
        sa.Column('diagnosis', sa.Text(), nullable=False),
        sa.Column('labor_cost', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('parts_cost', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('other_fees', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('expected_completion_time', sa.String(length=255), nullable=False),
        sa.Column('warranty_duration', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('before_repair_images', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='PENDING', nullable=False),
        sa.Column('customer_notes', sa.Text(), nullable=True),
        sa.Column('clarification_message', sa.Text(), nullable=True),
        sa.Column('clarification_response', sa.Text(), nullable=True),
        sa.Column('clarification_requested_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['repair_id'], ['repairs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['technician_id'], ['technician_profiles.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quotes_id'), 'quotes', ['id'], unique=False)

    # 11. Parts table
    op.create_table(
        'parts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sku', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('manufacturer', sa.String(length=100), nullable=False),
        sa.Column('condition', sa.String(length=50), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('stock', sa.Integer(), server_default='0', nullable=False),
        sa.Column('warranty_days', sa.Integer(), server_default='90', nullable=False),
        sa.Column('seller_name', sa.String(length=255), server_default='ReVivo Verified Supplier', nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('compatible_brands', sa.JSON(), nullable=True),
        sa.Column('compatible_models', sa.JSON(), nullable=True),
        sa.Column('compatible_categories', sa.JSON(), nullable=True),
        sa.Column('is_oem', sa.Boolean(), server_default=sa.text('0'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('1'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parts_id'), 'parts', ['id'], unique=False)
    op.create_index(op.f('ix_parts_sku'), 'parts', ['sku'], unique=True)

    # 12. Notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default=sa.text('0'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)

    # 13. Payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('repair_id', sa.Integer(), nullable=True),
        sa.Column('order_reference', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), server_default='USD', nullable=False),
        sa.Column('state', sa.String(length=50), server_default='CREATED', nullable=False),
        sa.Column('payment_provider', sa.String(length=50), server_default='sandbox', nullable=False),
        sa.Column('provider_transaction_id', sa.String(length=255), nullable=True),
        sa.Column('provider_intent_id', sa.String(length=255), nullable=True),
        sa.Column('payment_method_type', sa.String(length=50), server_default='card', nullable=False),
        sa.Column('last_four', sa.String(length=4), nullable=True),
        sa.Column('card_brand', sa.String(length=50), nullable=True),
        sa.Column('platform_fee', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('technician_payout', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('invoice_reference', sa.String(length=100), nullable=False),
        sa.Column('failure_reason', sa.String(length=255), nullable=True),
        sa.Column('refund_reference', sa.String(length=100), nullable=True),
        sa.Column('refund_amount', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['repair_id'], ['repairs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    op.create_index(op.f('ix_payments_invoice_reference'), 'payments', ['invoice_reference'], unique=True)
    op.create_index(op.f('ix_payments_order_reference'), 'payments', ['order_reference'], unique=True)


def downgrade() -> None:
    op.drop_table('payments')
    op.drop_table('notifications')
    op.drop_table('parts')
    op.drop_table('quotes')
    op.drop_table('repair_history')
    op.drop_table('repairs')
    op.drop_table('decisions')
    op.drop_table('diagnostics')
    op.drop_table('device_images')
    op.drop_table('devices')
    op.drop_table('technician_profiles')
    op.drop_table('blacklisted_tokens')
    op.drop_table('users')
