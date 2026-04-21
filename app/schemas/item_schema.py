from pydantic import BaseModel, ConfigDict, Field, computed_field


class ItemBase(BaseModel):
    """Base schema of Item"""
    name: str = Field(min_length=3, max_length=50)
    description: str | None = None
    price: float = Field(ge=0)
    tax: float | None = None

class ItemPydantic(ItemBase):
    """Public schema of Item model"""
    id: int
    owner_id: int

    @computed_field
    @property
    def total_price(self) -> float:
        """Function to calculate total price of an item including tax"""
        return (self.price or 0) + (self.tax or 0)
    
    model_config = ConfigDict(from_attributes=True)

class ItemCreate(ItemBase):
    """Schema for Item creation"""
    pass

class ItemUpdate(ItemBase):
    """Schema for Item update"""
    name: str | None = Field(default=None, min_length=3, max_length=50)
    description: str | None = None
    price: float | None = Field(default=None, ge=0)
    tax: float | None = None

class ItemInDB(ItemBase):
    """Schema to represent Item in Database"""
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)