from flask import redirect, render_template, url_for, current_app, flash, request, session
from shop import db, app, photos
import secrets, os

from .models import Brand, Category, Product
from .forms import Addproducts


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter(Product.stock > 0).order_by(Product.id.desc()).paginate(page=page, per_page=4)
    brands = Brand.query.join(Product, Brand.id == Product.brand_id).all()
    categories = Category.query.join(Product, Category.id == Product.category_id).all()
    return render_template('products/index.html', products=products, brands=brands, categories=categories)


@app.route('/product/<int:id>')
def single_page(id):
    product = Product.query.get_or_404(id)
    return render_template('products/single_page.html', product=product)


@app.route('/brand/<int:id>')
def get_brand(id):
    page = request.args.get('page', 1, type=int)
    get_br = Brand.query.filter_by(id=id).first_or_404()
    brand = Product.query.filter_by(brand=get_br).paginate(page=page, per_page=4)
    brands = Brand.query.join(Product, Brand.id == Product.brand_id).all()
    categories = Category.query.join(Product, Category.id == Product.category_id).all()
    return render_template('products/index.html', brand=brand, brands=brands, categories=categories, get_br=get_br)


@app.route('/category/<int:id>')
def get_category(id):
    page = request.args.get('page', 1, type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    category = Product.query.filter_by(category=get_cat).paginate(page=page, per_page=4)
    brands = Brand.query.join(Product, Brand.id == Product.brand_id).all()
    categories = Category.query.join(Product, Category.id == Product.category_id).all()
    return render_template('products/index.html', category=category, categories=categories, brands=brands, get_cat=get_cat)


@app.route('/addbrand', methods=["GET", "POST"])
def addbrand():
    if 'email' not in session:
        flash('Please, login first!', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        db.session.commit()
        flash(f'The Brand {getbrand} was added to your database.', 'success')
        return redirect(url_for('addbrand'))

    return render_template('products/addbrand.html', brands='brands')


@app.route('/updatebrand/<int:id>', methods=["GET", 'POST'])
def updatebrand(id):
    if 'email' not in session:
        flash('Please, login first!', 'danger')
        return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method == "POST":
        updatebrand.name = brand
        flash('Your brand has been updated')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/updatebrand.html', title='Update Brand Page', updatebrand=updatebrand)


@app.route('/updatecategory/<int:id>', methods=["GET", 'POST'])
def updatecategory(id):
    if 'email' not in session:
        flash('Please, login first!', 'danger')
        return redirect(url_for('login'))
    updatecategory = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == "POST":
        updatecategory.name = category
        flash('Your category has been updated')
        db.session.commit()
        return redirect(url_for('categories'))
    return render_template('products/updatebrand.html', title='Update Category Page', updatecategory=updatecategory)


@app.route('/addcategory', methods=["GET", "POST"])
def addcategory():
    if 'email' not in session:
        flash('Please, login first!', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        getcategory = request.form.get('category')
        category = Category(name=getcategory)
        db.session.add(category)
        db.session.commit()
        flash(f'The Category {getcategory} was added to your database.', 'success')
        return redirect(url_for('addcategory'))

    return render_template('products/addbrand.html', brands='categories')


@app.route('/addproduct', methods=["POST", "GET"])
def addproduct():
    brands = Brand.query.all()
    categories = Category.query.all()
    form = Addproducts(request.form)
    if 'email' not in session:
        flash('Please, login first!', 'danger')
        return redirect(url_for('login'))
    if request.method == "POST":
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        colors = form.colors.data
        description = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')
        addprod = Product(name=name, price=price, discount=discount, stock=stock, colors=colors,
                              description=description, brand_id=brand, category_id=category, image_1=image_1,
                              image_2=image_2, image_3=image_3)
        db.session.add(addprod)
        flash(f'The Product {name} has been added to your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('products/addproduct.html', title='Add Product page', form=form, brands=brands, categories=categories)


@app.route('/updateproduct/<int:id>', methods=["GET", "POST"])
def updateproduct(id):
    categories = Category.query.all()
    brands = Brand.query.all()
    product = Product.query.get_or_404(id)
    brand = request.form.get('brand')
    category = request.form.get('category')
    form = Addproducts(request.form)
    if request.method == "POST":
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.brand_id = brand
        product.categoty_id = category
        product.colors = form.colors.data
        product.description = form.description.data
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/' + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + '.')

        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/' + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + '.')

        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, 'static/images/' + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + '.')
        db.session.commit()
        flash('You product has been updates', 'success')
        return redirect(url_for('admin'))
    form.name.data = product.name
    form.price.data = product.price
    form.description.data = product.description
    form.stock.data = product.stock
    form.colors.data = product.colors
    form.discount.data = product.discount
    return render_template('products/updateproduct.html', form=form, brands=brands, categories=categories, product=product)


@app.route('/deletebrand/<int:id>', methods=['POST'])
def deletebrand(id):
    brand = Brand.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(brand)
        flash(f'The brand {brand.name} was deleted form your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    flash(f"The brand {brand.name} can't be deleted ", 'warning')
    return redirect(url_for('admin'))


@app.route('/deletecategory/<int:id>', methods=['POST'])
def deletecategory(id):
    category = Category.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(category)
        flash(f'The brand {category.name} was deleted form your database', 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    flash(f"The brand {category.name} can't be deleted ", 'warning')
    return redirect(url_for('admin'))


@app.route('/deleteproduct/<int:id>',  methods=["POST"])
def deleteproduct(id):
    product = Product.query.get_or_404(id)
    if request.method == "POST":
        try:
            os.unlink(os.path.join(current_app.root_path, 'static/images/' + product.image_1))
            os.unlink(os.path.join(current_app.root_path, 'static/images/' + product.image_2))
            os.unlink(os.path.join(current_app.root_path, 'static/images/' + product.image_3))
        except Exception as e:
            print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f'Продукт {product.name} был удален успешно', 'success')
        return redirect(url_for('admin'))
    flash(f'Невозможно удалить {product.name}')
    return redirect(url_for('admin'))
